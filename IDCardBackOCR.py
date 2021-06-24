import time
import cv2
from cnocr import CnOcr
import json


class IDCardBackOCR:
    def idCard_back_ocr(self):
        """
        识别身份证背面信息

        :return: 识别出的json数据
        """
        time1 = time.time()

        img = cv2.imread('static/pic/img.jpg', 0)

        # 调用ocr模型
        ocr = CnOcr(name="ocr")  # 识别中文
        ocr_num = CnOcr(name="num")  # 识别数字
        ocr_num.set_cand_alphabet({'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'})

        # 裁剪签发机构区域并识别
        office_img = img[275:310, 255:410]
        office = ocr.ocr_for_single_line(office_img)
        office = "".join(office)

        # 裁剪有效期区域并识别
        date_img = img[325:365, 250:520]
        date = ocr_num.ocr_for_single_line(date_img)
        date.insert(4, '.')
        date.insert(7, '.')
        date.insert(10, '-')
        date.insert(15, '.')
        date.insert(18, '.')
        date = "".join(date)

        # 将识别出的信息组成json数据
        json_data = {"office": office, "date": date, "card_type": 'idCard_back'}
        res = json.dumps(json_data, ensure_ascii=False)
        time2 = time.time()
        print('OCR时间：' + str(time2 - time1))
        return res
