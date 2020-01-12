# coding:utf-8
import os

import PIL
from PIL import Image, ImageOps, ImageFilter
import numpy as np

# 待处理图片地址
data_path = r'E:\DeepLearnSample\EdgeConnect\mask\qd_imd\test'
# 保存图片的地址
save_path = r'E:\DeepLearnSample\EdgeConnect\mask\CustomMask3\test'


def image_resize(new_img, size):
    new_img = new_img.resize(size, Image.ANTIALIAS)  # 改变图片大小
    return new_img


def image_invert_color(new_img):
    matrix = np.asarray(new_img)  # 图像转矩阵
    matrix = 255 - matrix  # 图像转矩阵 并反色
    new_img = Image.fromarray(matrix)  # 矩阵转图像
    # new_img = ImageOps.invert(new_img)  # 反色
    return new_img


def image_save(new_img, savePath, image_name, image_type=None):
    if image_type:
        image_type = image_type  # 保存的图片格式
        image_file = image_name.split('.', 1)[0] + '.' + image_type  # 保存的图片名字
        new_img.save(savePath + '/' + image_file, image_type)  # 保存图片
        return savePath + '/' + image_file
    else:
        new_img.save(savePath + '/' + image_name)  # 保存图片
        return savePath + '/' + image_name


def image_process(imgPath, savePath):
    files = os.listdir(imgPath)
    files.sort()
    print('Data Path :', imgPath)
    print('Save Path :', savePath)
    print('start...')

    img_num = len(files)
    for index, file in enumerate(files):
        new_img = Image.open(imgPath + '/' + file)  # 打开图片
        # new_img = image_resize(new_img, (1024, 1024)) # 改变图片大小
        # new_img = new_img.convert('RGB')  # 改变格式
        new_img = new_img.convert('L')  # 改变格式
        # new_img = new_img.filter(ImageFilter.BLUR)  # 高斯模糊
        new_img = image_invert_color(new_img)
        new_img = new_img.convert('1')  # 改变格式 只存在黑白

        image_path = image_save(new_img, savePath, file)

        print(index+1, '/', img_num, '  process image : ', imgPath + '/' + file, '  save image : ', image_path)

    print('done!')


if __name__ == '__main__':
    image_process(data_path, save_path)
