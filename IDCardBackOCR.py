import time
import FindCard
from cnocr import CnOcr
import json


class IDCardBackOCR:
    def idCard_back_ocr(self, img0):
        """
        识别身份证背面信息

        :param img0: 待识别身份证路径及名称str
        :return: 识别出的json数据
        """
        time1 = time.time()
        # 查找身份证轮廓并裁剪
        find = FindCard.FindCard()
        img = find.find('template/idcard_back.jpg', img0)

        # 调用ocr模型
        ocr = CnOcr(name="ocr")  # 识别中文
        ocr_num = CnOcr(name="num")  # 识别数字
        ocr_num.set_cand_alphabet({'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'})

        # 裁剪签发机构区域并识别
        office_img = img[275:310, 260:410]
        office = ocr.ocr_for_single_line(office_img)
        office = "".join(office)

        # 裁剪有效期区域并识别
        date_img = img[325:365, 255:520]
        date = ocr_num.ocr_for_single_line(date_img)
        date = "".join(date)

        # 将识别出的信息组成json数据
        json_data = {"office": office, "date": date}
        res = json.dumps(json_data, ensure_ascii=False)
        time2 = time.time()
        print(time2 - time1)
        return res


if __name__ == '__main__':
    ocr = IDCardBackOCR()
    res = ocr.idCard_back_ocr('pic/12.jpg')
    print(res)
