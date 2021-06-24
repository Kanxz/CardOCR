import numpy as np
import cv2
import time


class FindCard:
    __FLANN_INDEX_KDTREE = 0
    # 启动 SIFT 检测器
    __sift = cv2.xfeatures2d.SIFT_create()
    # 关键点
    __good = []
    __kp1 = None
    __kp2 = None
    __des2 = None

    def img_resize(self, img_gray, d_width):
        """
        调整图片大小

        :param img_gray: 灰度图片
        :param d_width: 需要调整到的宽度
        :return: 调整后的图片
        """
        crop = img_gray
        size = crop.shape
        height = size[0]
        width = size[1]
        height = height * d_width / width
        crop = cv2.resize(src=crop, dsize=(d_width, int(height)), interpolation=cv2.INTER_CUBIC)
        return crop

    def find_key_points(self, img1):
        """
        匹配模板图和待识别图片的特征点，如果匹配到的特征点数量过少返回False

        :param img1: 模板图相对路径str
        :return: bool
        """
        # 使用 SIFT 找到关键点和描述符
        self.__kp1, des1 = self.__sift.detectAndCompute(img1, None)

        index_params = dict(algorithm=self.__FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=10)
        # 匹配目标图和模板图的关键点
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(des1, self.__des2, k=2)

        # 两个最佳匹配之间距离需要大于ratio 0.7,距离过于相似可能是噪声点
        list.clear(self.__good)
        for m, n in matches:
            if m.distance < 0.7 * n.distance:
                self.__good.append(m)

        if len(self.__good) > 25:
            return True
        return False

    def find(self, img_name):
        """
        分类查找并裁剪出证件照的轮廓，返回裁剪好的图片和类型，如果无法识别，类型返回为other

        :param img_name: 待裁剪图片文件名str，相对路径
        :return: 裁剪好的证件照图片，证件照类型
        """
        # 读取灰度模板图片
        idCard_front = cv2.imread('card/idcard_front.jpg')
        idCard_back = cv2.imread('card/idcard_back.jpg')
        seCard_front = cv2.imread('card/secard_front.jpg')
        seCard_back = cv2.imread('card/secard_back.jpg')

        img2 = cv2.imread(img_name, 0)
        img2 = self.img_resize(img2, 1920)

        img_org = cv2.imread(img_name)  # 读取原图并调整大小
        img_org = self.img_resize(img_org, 1920)

        # 双边滤波减少噪声点
        img2 = cv2.bilateralFilter(img2, 9, 75, 75)

        time1 = time.time()

        self.__kp2, self.__des2 = self.__sift.detectAndCompute(img2, None)

        # 判断是什么类型的图片
        if self.find_key_points(idCard_front):
            card_type = 'idCard_front'
        elif self.find_key_points(idCard_back):
            card_type = 'idCard_back'
        elif self.find_key_points(seCard_back):
            card_type = 'seCard_back'
        elif self.find_key_points(seCard_front):
            card_type = 'seCard_front'
        else:
            card_type = 'other'
            time2 = time.time()
            print(time2 - time1)
            return None, card_type

        time2 = time.time()
        print('分类时间：' + str(time2 - time1))

        src_pts = np.float32([self.__kp1[m.queryIdx].pt for m in self.__good]).reshape(-1, 1, 2)
        dst_pts = np.float32([self.__kp2[m.trainIdx].pt for m in self.__good]).reshape(-1, 1, 2)

        # 用HomoGraphy计算图像与图像之间映射关系, M为转换矩阵
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        # 使用转换矩阵M计算出img1在img2的对应形状
        M_r = np.linalg.inv(M)

        # 透视变化
        im_r = cv2.warpPerspective(img_org, M_r, (640, 405))

        return im_r, card_type
