import findIDCard
import cv2
from cnocr import CnOcr
import json
import time


class IDCardOCR:
    def idCard_ocr(self, img0):
        """
        读取身份证正面信息

        :param img0: 图片地址str
        :return: json数据
        """
        time1 = time.time()

        # 识别身份证照片的轮廓，并裁剪出来
        find = findIDCard.findIDCard()
        img = find.find(img0)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)  # 图片灰度化

        # 调用cnocr模型进行文字识别
        ocr = CnOcr(name='ocr')

        # 对裁剪出来的图片裁剪出姓名区域，并对该区域进行识别
        name_img = img[50:90, 115:240]
        name = ocr.ocr_for_single_line(name_img)
        name = "".join(name)

        # 对裁剪出来的图片裁剪出性别区域，并对该区域进行识别
        sex_img = img[100:140, 115:160]
        sex = ocr.ocr_for_single_line(sex_img)
        sex = "".join(sex)

        # 对裁剪出来的图片裁剪出名族区域，并对该区域进行识别
        nation_img = img[110:140, 250:330]
        nation = ocr.ocr_for_single_line(nation_img)
        nation = "".join(nation)

        # 对裁剪出来的图片裁剪出地址区域，并对该区域进行识别
        address_img = img[200:310, 110:400]
        # 二值化，提高识别准确率
        # _, address_img = cv2.threshold(address_img, 150, 255, cv2.THRESH_BINARY)
        # 自适应阈值化
        address_img = cv2.adaptiveThreshold(address_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY, 21, 25)
        tmp = ocr.ocr(address_img)
        address = ""
        for i in range(len(tmp)):
            tmp1 = "".join(tmp[i])
            address = address + tmp1

        ocr_id = CnOcr(name='ID')
        # 限定ocr识别的范围
        ocr_id.set_cand_alphabet({'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'X'})

        # 裁剪出身份证号码区域，并识别
        id_img = img[330:380, 210:580]
        _, id_img = cv2.threshold(id_img, 80, 255, cv2.THRESH_BINARY)
        ID = ocr_id.ocr_for_single_line(id_img)
        ID = "".join(ID)

        # 返回json数据
        json_data = {"name": name,
                     "sex": sex,
                     "nation": nation,
                     "address": address,
                     "ID": ID}
        # print(json_data)
        res = json.dumps(json_data, ensure_ascii=False)
        time2 = time.time()
        print(time2 - time1)
        return res


if __name__ == '__main__':
    id_card_ocr = IDCardOCR()
    # img = cv2.imread("1.jpg")
    res = id_card_ocr.idCard_ocr("pic/4.jpg")
    print(res)
