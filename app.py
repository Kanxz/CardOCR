import os
from datetime import timedelta
from flask import Flask, render_template, request
import IDCardFrontOCR
import json
import requests
import socket
import re
import imghdr

# 符合条件的图片后缀
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    """
    判断文件后缀是否符合条件

    :param filename: 文件名
    :return: bool
    """
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


app = Flask(__name__)

# 设置静态缓存过期时间
app.send_file_max_age_default = timedelta(seconds=1)
# 获取路径
path = os.path.dirname(__file__) + '/static/pic/'
# 设定无响应时间，防止有的坏图片长时间没办法下载下来
timeout = 20
socket.setdefaulttimeout(timeout)

IDCardFrontOCR = IDCardFrontOCR.IDCardFrontOCR()


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
    # 获取上传的图片
    img_data = request.files['photo']
    # 判断图片后缀是否合法
    if not (img_data and allowed_file(img_data.filename)):
        return render_template('index.html', msg='请检查上传的图片类型，仅限于png、jpg、jpeg')

    # 保存图片到本地
    img_data.save(path + 'img.jpg')

    json_res = IDCardFrontOCR.idCard_front_ocr("static/pic/img.jpg")

    json_dict = json.loads(json_res)
    res = '姓名：' + json_dict['name'] + '\n' \
          + '性别：' + json_dict['gender'] + '\n' \
          + '民族：' + json_dict['nation'] + '\n' \
          + '地址：' + json_dict['address'] + '\n' \
          + '身份证号码：' + json_dict['ID'] + '\n'
    return render_template('index.html', img='static/pic/img.jpg', res=res, json=json_res)


@app.route('/url_upload', methods=['POST'])
def url_upload():
    """
    url上传图片
    """
    # 获取url
    url = request.form['text']

    # 判断url是否合法
    if not re.match(r'^https?:/{2}\w.+$', url):
        return render_template('index.html', msg='无法下载图片，图片URL错误或者无效，请检查URL')

    # 将文件保存到本地并重命名
    img_data = requests.get(url)
    with open(path + 'img.jpg', 'wb') as f:
        f.write(img_data.content)

    # 判断该文件是否为合法图片
    img_type = imghdr.what(path + 'img.jpg')
    if not (img_type in ALLOWED_EXTENSIONS):
        return render_template('index.html', msg='请检查上传的图片类型，仅限于png、jpg、jpeg')

    json_res = IDCardFrontOCR.idCard_front_ocr("static/pic/img.jpg")
    json_dict = json.loads(json_res)
    res = '姓名：' + json_dict['name'] + '\n' \
          + '性别：' + json_dict['gender'] + '\n' \
          + '民族：' + json_dict['nation'] + '\n' \
          + '地址：' + json_dict['address'] + '\n' \
          + '身份证号码：' + json_dict['ID'] + '\n'
    return render_template('index.html', img='static/pic/img.jpg', res=res, json=json_res)


if __name__ == '__main__':
    app.run()
