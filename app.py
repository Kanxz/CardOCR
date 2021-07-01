import os
import time
from datetime import timedelta
import cv2
from flask import Flask, render_template, request
import FindCard
import IDCardBackOCR
import IDCardFrontOCR
import SECardFrontOCR
import json
import requests
import re
import imghdr

# 符合条件的图片后缀
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)

# 设置静态缓存过期时间
app.send_file_max_age_default = timedelta(seconds=1)
# 获取路径
path = os.path.dirname(__file__) + '/static/pic/'

FindCard = FindCard.FindCard()
IDCardFrontOCR = IDCardFrontOCR.IDCardFrontOCR()
IDCardBackOCR = IDCardBackOCR.IDCardBackOCR()
SECardFrontOCR = SECardFrontOCR.SECardFrontOCR()


def allowed_file(filename):
    """
    判断文件后缀是否符合条件

    :param filename: 文件名
    :return: bool
    """
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def card_ocr(card_type):
    """
    根据card_type进行OCR识别，并返回识别出的相应的字符串，json和dict

    :param card_type: 卡片类型
    :return: 字符串，json数据，dict数据
    """
    res = ''
    json_res = None
    json_dict = None

    if card_type is 'idCard_front':
        json_res = IDCardFrontOCR.idCard_front_ocr()
        json_dict = json.loads(json_res)
        res = '姓名：' + json_dict['name'] + '\n' \
              + '性别：' + json_dict['gender'] + '\n' \
              + '民族：' + json_dict['nation'] + '\n' \
              + '生日：' + json_dict['birth'] + '\n' \
              + '地址：' + json_dict['address'] + '\n' \
              + '身份证号码：' + json_dict['ID'] + '\n' \
              + '身份证号码合法性：' + str(json_dict['legality']) + '\n' \
              + '类型：身份证头像面'

    elif card_type is 'idCard_back':
        json_res = IDCardBackOCR.idCard_back_ocr()
        json_dict = json.loads(json_res)
        res = '签发机关：' + json_dict['office'] + '\n' \
              + '有效期限：' + json_dict['date'] + '\n' \
              + '类型：身份证国徽面'

    elif card_type is 'seCard_front':
        json_res = SECardFrontOCR.seCard_front_OCR()
        json_dict = json.loads(json_res)
        res = '姓名：' + json_dict['name'] + '\n' \
              + '社会保障号码：' + json_dict['se_id'] + '\n' \
              + '发卡日期：' + json_dict['date'] + '\n' \
              + '银行卡号：' + json_dict['bank_id'] + '\n' \
              + '类型：社保卡头像面'

    elif card_type is 'seCard_back':
        res = '类型：社保卡国徽面'
        json_dict = {'card_type': 'seCard_back'}
        json_res = json.dumps(json_dict)

    return res, json_res, json_dict


@app.route('/', methods=['GET'])
def home():
    """
    主页
    """
    return render_template('index.html')


@app.route('/file_upload', methods=['POST'])
def file_upload():
    """
    本地文件上传
    """
    time1 = time.time()
    # 获取上传的图片
    img_data = request.files['photo']

    # 判断文件大小
    size = len(img_data.read()) / (1024 * 1024)
    if size > 5:
        return render_template('index.html', msg='图片过大，请限制在 5M 之内')

    img_data.seek(0)

    # 判断图片后缀是否合法
    if not (img_data and allowed_file(img_data.filename)):
        return render_template('index.html', msg='请检查上传的图片类型\n仅限于：png、jpg、jpeg')

    # 保存图片到本地
    img_data.save(path + 'img0.jpg')

    # 分类，裁剪图片
    img, card_type = FindCard.find('static/pic/img0.jpg')
    if card_type == 'other':
        return render_template('index.html', msg='该图片无法识别\n请确保上传：身份证图片或社保卡图片\n或是图片过于模糊')

    cv2.imwrite('static/pic/img.jpg', img)  # 保存图片到本地

    # OCR识别
    res, json_res, json_dict = card_ocr(card_type)

    time2 = time.time()
    print('总耗时：' + str(time2 - time1))
    # 添加用时项
    time_used = round(time2 - time1, 3)
    ip = request.remote_addr  # 获取IP
    res_dict = {'IP': ip, 'time_used': time_used, 'card': json_dict}
    json_res = json.dumps(res_dict)

    return render_template('index.html', img='static/pic/img.jpg', res=res, json=json_res)


@app.route('/url_upload', methods=['POST'])
def url_upload():
    """
    url上传图片
    """
    time1 = time.time()
    # 获取url
    url = request.form['text']

    # 判断url是否合法
    if not re.match(r'^https?:/{2}\w.+$', url):
        return render_template('index.html', msg='无法加载图片，图片URL错误或者无效，请检查 URL')

    try:
        img_data = requests.get(url, timeout=5)  # 判断请求是否超时
    except requests.exceptions.ReadTimeout:
        return render_template('index.html', msg='请求超时，请重新选择 URL')

    # 判断文件大小
    size = len(img_data.content) / (1024 * 1024)
    if size > 5:
        return render_template('index.html', msg='图片过大，请限制在 5M 之内')

    # 将文件保存到本地并重命名
    with open(path + 'img0.jpg', 'wb') as f:
        f.write(img_data.content)

    # 判断该文件是否为合法图片
    img_type = imghdr.what(path + 'img0.jpg')
    if not (img_type in ALLOWED_EXTENSIONS):
        return render_template('index.html', msg='请检查上传的图片类型\n仅限于：png、jpg、jpeg')

    # 分类，裁剪图片
    img, card_type = FindCard.find('static/pic/img0.jpg')
    if card_type == 'other':
        return render_template('index.html', msg='该图片无法识别\n请确保上传：身份证图片或社保卡图片\n或是图片过于模糊')

    cv2.imwrite('static/pic/img.jpg', img)

    res, json_res, json_dict = card_ocr(card_type)

    time2 = time.time()
    print('总耗时：' + str(time2 - time1))
    time_used = round(time2 - time1, 3)
    ip = request.remote_addr
    res_dict = {'IP': ip, 'time_used': time_used, 'card': json_dict}
    json_res = json.dumps(res_dict)

    return render_template('index.html', img='static/pic/img.jpg', res=res, json=json_res)


if __name__ == '__main__':
    app.run()
