# coding:utf-8

import numpy as np
from PIL import Image
from skimage import data, filters
from skimage.color import rgb2gray, gray2rgb
from skimage.feature import canny

# 待处理图片地址
# data_path = r'E:\DeepLearningData\Raw\test.png'
# data_path = r'E:\DeepLearningData\Raw\Cartoon\CartoonCensored\danbooru\2565144.png'
data_path = r'E:\DeepLearningData\Raw\Cartoon\CartoonCensored\danbooru\2573882.png'

def mosaic_detect(img_data):
    img_data = rgb2gray(img_data)
    # img_data = filters.sobel(img_data)
    img_data = filters.roberts(img_data)
    # img_data = filters.scharr(img_data)
    # img_data = filters.prewitt(img_data)
    # img_data = canny(img_data, sigma=0.1).astype(np.float)
    img_data = ((img_data>0.03).astype(np.uint8) * 255)
    pil_img = Image.fromarray(img_data)
    pil_img.show()


if __name__ == '__main__':
    new_img = Image.open(data_path)  # 打开图片
    img_data = np.asarray(new_img)  # 图像转矩阵
    mosaic_detect(img_data)
