import os
import argparse
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--path', type=str, help='path to the dataset')
parser.add_argument('--output', type=str, help='path to the file list')
args = parser.parse_args()

ext = {'.JPG', '.JPEG', '.PNG', '.TIF', 'TIFF'}

flist_dataset_paths = [
    (r"../datasets/places2_train.flist", r"E:\DeepLearnSample\EdgeConnect\CelebA\train"),
    (r"../datasets/places2_val.flist",   r"E:\DeepLearnSample\EdgeConnect\CelebA\eval"),
    (r"../datasets/places2_test.flist",  r"E:\DeepLearnSample\EdgeConnect\CelebA\test"),
    (r"../datasets/masks_train.flist", r"E:\DeepLearnSample\EdgeConnect\mask\CustomMask3\train"),
    (r"../datasets/masks_val.flist",   r"E:\DeepLearnSample\EdgeConnect\mask\CustomMask3\eval"),
    (r"../datasets/masks_test.flist",  r"E:\DeepLearnSample\EdgeConnect\mask\CustomMask2\test"),
]

for flist_path, dataset_path in flist_dataset_paths:
    print('creating', flist_path)
    images = []

    # auto create directory
    os.makedirs(os.path.dirname(flist_path), exist_ok=True)

    # find all image
    for root, dirs, files in os.walk(dataset_path):
        print('loading : ' + root)
        for file in files:
            # print('image : ' + file)
            if os.path.splitext(file)[1].upper() in ext:
                images.append(os.path.join(root, file))

    images = sorted(images)
    np.savetxt(flist_path, images, fmt='%s')