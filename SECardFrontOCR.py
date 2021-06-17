import FindCard
from cnocr import CnOcr, NUMBERS, ENG_LETTERS
from skimage import io
import cv2
import json


class SECardFrontOCR:
    def seCard_front_OCR(self, img0):
        """
        读取社保卡正面（照片面）信息

        :param img0: 待识别图片地址str
        :return: json数据
        """

        # 目标提取
        find = FindCard.FindCard()
        img = find.find('template/secard_front.jpg', img0)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        # 调用ocr模型
        ocr = CnOcr(name="ocr")  # 识别中文
        ocr_num = CnOcr(name="num")  # 识别数字
        ocr_id = CnOcr(name="id")
        ocr_num.set_cand_alphabet({'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'})
        ocr_num.set_cand_alphabet({'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'X'})

        # 裁剪姓名区域，并对该区域进行识别
        name_img = img[110:135, 265:340]
        name = ocr.ocr_for_single_line(name_img)
        name = "".join(name)

        # 裁剪社会保障号码区域，并对该区域进行识别
        SE_ID_img = img[140:165, 345:545]
        SE_ID = ocr_id.ocr_for_single_line(SE_ID_img)
        SE_ID = "".join(SE_ID)

        # 裁剪发卡日期区域，并对该区域进行识别
        date_img = img[175:200, 300:415]
        date = ocr_num.ocr_for_single_line(date_img)
        date = "".join(date)

        # 裁剪银行卡号区域，并对该区域进行识别
        account_num_img = img[280:340, 110:590]
        account_num = ocr_num.ocr_for_single_line(account_num_img)
        account_num = "".join(account_num)

        # 返回json数据
        json_data = {"姓名": name,
                     "社会保障号码": SE_ID,
                     "发卡日期": date,
                     "银行卡号": account_num}
        res = json.dumps(json_data, ensure_ascii=False)
        return res


if __name__ == '__main__':
    se_card_ocr = SECardFrontOCR()
    res = se_card_ocr.seCard_front_OCR("pic/e.jpg")
    print(res)
