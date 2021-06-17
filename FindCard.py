import numpy as np
import cv2


class FindCard:
    def img_resize(self, imggray, dwidth):
        """
        调整图片大小

        :param imggray: 灰度图片
        :param dwidth: 需要调整到的宽度
        :return: 调整后的图片
        """
        crop = imggray
        size = crop.shape
        height = size[0]
        width = size[1]
        height = height * dwidth / width
        crop = cv2.resize(src=crop, dsize=(dwidth, int(height)), interpolation=cv2.INTER_CUBIC)
        return crop

    def find(self, img1_name, img2_name):
        """
        查找并裁剪出身份证的轮廓

        :param img1_name: 模板图片文件名str，相对路径
        :param img2_name: 待裁剪图片文件名str，相对路径
        :return: 查找到的身份证图片
        """
        img1 = cv2.imread(img1_name, 0)  # 读取灰度图片并调整大小
        img1 = self.img_resize(img1, 640)

        img2 = cv2.imread(img2_name, 0)
        img2 = self.img_resize(img2, 1920)

        img_org = cv2.imread(img2_name)  # 读取原图并调整大小
        img_org = self.img_resize(img_org, 1920)

        # 启动 SIFT 检测器
        sift = cv2.xfeatures2d.SIFT_create()
        # 使用 SIFT 找到关键点和描述符
        kp1, des1 = sift.detectAndCompute(img1, None)
        kp2, des2 = sift.detectAndCompute(img2, None)

        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=10)
        # 匹配目标图和模板图的关键点
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(des1, des2, k=2)

        # 两个最佳匹配之间距离需要大于ratio 0.7,距离过于相似可能是噪声点
        good = []
        for m, n in matches:
            if m.distance < 0.7 * n.distance:
                good.append(m)

        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

        # 用HomoGraphy计算图像与图像之间映射关系, M为转换矩阵
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        # 使用转换矩阵M计算出img1在img2的对应形状
        h, w = img1.shape
        M_r = np.linalg.inv(M)

        # 透视变化
        im_r = cv2.warpPerspective(img_org, M_r, (w, h))

        return im_r


if __name__ == '__main__':
    img = FindCard().find('card/idcard_front.jpg', 'pic/1.jpg')
    cv2.imshow('img', img)
    cv2.waitKey()
