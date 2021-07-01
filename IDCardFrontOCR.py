import cv2
from cnocr import CnOcr
import json
import time


class IDCardFrontOCR:
    def id_check(self, id_num, birth):
        """
        判断身份证号码是否合法

        :param birth: 初试日期
        :param id_num: 身份证号码str
        :return: bool
        """
        if len(id_num) != 18:
            return False

        # 身份证与出生日期是否匹配
        year, month, day = birth.split('-', 2)
        if len(month) is 1:
            month = '0' + month
        if len(day) is 1:
            day = '0' + day
        new_birth = year + month + day
        if id_num[6:14] != new_birth:
            return False

        # 身份证前17位权值
        weight = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        # 检验码取值范围，与下标对应
        value = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
        count = 0
        for index in range(17):
            count = count + int(id_num[index]) * weight[index]
        if value[count % 11] == id_num[17]:
            return True
        else:
            return False

    def idCard_front_ocr(self):
        """
        读取身份证正面信息

        :return: json数据
        """
        time1 = time.time()

        img = cv2.imread('static/pic/img.jpg', 0)

        # 调用cnocr模型进行文字识别
        ocr = CnOcr(name='ocr')

        # 裁剪姓名区域，并对该区域进行识别
        name_img = img[50:90, 115:240]
        name = ocr.ocr_for_single_line(name_img)
        name = "".join(name)

        # 裁剪民族区域，并对该区域进行识别
        nation_img = img[110:140, 250:330]
        nation = ocr.ocr_for_single_line(nation_img)
        nation = "".join(nation)

        # 获取数字识别的ocr
        ocr_num = CnOcr(name='ID')
        ocr_num.set_cand_alphabet({'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'})

        # 裁剪年月日区域，并识别
        year_img = img[160:190, 120:185]
        year_img = cv2.adaptiveThreshold(year_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY, 45, 30)
        year = ocr_num.ocr_for_single_line(year_img)
        year = "".join(year)

        month_img = img[160:190, 210:250]
        month_img = cv2.adaptiveThreshold(month_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          cv2.THRESH_BINARY, 45, 30)
        month = ocr_num.ocr_for_single_line(month_img)
        month = "".join(month)

        day_img = img[160:190, 275:310]
        day_img = cv2.adaptiveThreshold(day_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY, 45, 30)
        day = ocr_num.ocr_for_single_line(day_img)
        day = "".join(day)
        birth = year + '-' + month + '-' + day

        # # 地址区域整体识别，识别正确率较低
        # # 裁剪地址区域，并对该区域进行识别
        # address_img = img[200:310, 120:400]
        # # 自适应阈值化
        # address_img = cv2.adaptiveThreshold(address_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        #                                     cv2.THRESH_BINARY, 81, 40)
        # tmp = ocr.ocr(address_img)
        # address = ""
        # for i in range(len(tmp)):
        #     tmp1 = "".join(tmp[i])
        #     address = address + tmp1

        # 地址区域分行识别，识别正确率较整体高
        address = ""
        # 裁剪地址区域，并对该区域进行识别
        address_img = img[210:242, 110:395]
        # 自适应阈值化
        address_img = cv2.adaptiveThreshold(address_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY, 57, 25)
        tmp = "".join(ocr.ocr_for_single_line(address_img))
        address = address + tmp

        address_img = img[240:280, 110:400]
        address_img = cv2.adaptiveThreshold(address_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY, 57, 25)
        tmp = "".join(ocr.ocr_for_single_line(address_img))
        address = address + tmp

        address_img = img[280:320, 110:400]
        address_img = cv2.adaptiveThreshold(address_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY, 45, 30)
        tmp = "".join(ocr.ocr_for_single_line(address_img))
        address = address + tmp

        ocr_id = CnOcr(name='ID')
        # 限定ocr识别的范围
        ocr_id.set_cand_alphabet({'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'X'})

        # 裁剪出身份证号码区域，并识别
        id_img = img[330:380, 210:580]
        _, id_img = cv2.threshold(id_img, 80, 255, cv2.THRESH_BINARY)
        ID = ocr_id.ocr_for_single_line(id_img)
        ID = "".join(ID)

        # 裁剪性别区域，并对该区域进行识别
        gender_img = img[100:140, 115:160]
        ocr.set_cand_alphabet({'男', '女'})
        gender = ocr.ocr_for_single_line(gender_img)
        gender = "".join(gender)

        # 返回json数据
        json_data = {"name": name,
                     "gender": gender,
                     "nation": nation,
                     "birth": birth,
                     "address": address,
                     "ID": ID,
                     "legality": self.id_check(ID, birth),
                     "card_type": 'idCard_front'}
        # print(json_data)
        res = json.dumps(json_data, ensure_ascii=False)
        time2 = time.time()
        print('OCR时间：' + str(time2 - time1))
        return res
