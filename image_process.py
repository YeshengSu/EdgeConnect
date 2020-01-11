# coding:utf-8
import os

import PIL
from PIL import Image, ImageOps
import numpy as np

# 待处理图片地址
dataPath = r'E:\DeepLearnSample\EdgeConnect\mask\qd_imd\train'
# 保存图片的地址
savePath = r'E:\DeepLearnSample\EdgeConnect\mask\CustomMask3\train'


def invert_color(imgPath, savePath):
    files = os.listdir(imgPath)
    files.sort()
    print('Data Path :', imgPath)
    print('Save Path :', savePath)
    print('start...')
    for index, file in enumerate(files):

        new_png = Image.open(imgPath + '/' + file)  # 打开图片
        # new_png = new_png.resize((20, 20),Image.ANTIALIAS) # 改变图片大小

        new_png = new_png.convert('L')  # 改变格式
        new_png = ImageOps.invert(new_png)  # 反色
        new_png = new_png.convert('1')  # 变为位图格式

        # matrix = np.asarray(new_png)  # 图像转矩阵
        # matrix = 255-matrix  # 图像转矩阵 并反色
        # new_png = Image.fromarray(matrix)  # 矩阵转图像

        new_png.save(savePath + '/' + file)  # 保存图片

        print('num', index, 'process image : ', imgPath + '\\' + file, '    save image : ', savePath + '\\' + file)
    print('done!')


if __name__ == '__main__':
    invert_color(dataPath, savePath)
