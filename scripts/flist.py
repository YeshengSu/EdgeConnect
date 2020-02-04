import os
import numpy as np

ext = {'.JPG', '.JPEG', '.PNG', '.TIF', 'TIFF'}

flist_dataset_paths = {
    r"../checkpoints/datasets/places2_train.flist": [r"E:\DeepLearningData\EdgeConnect\CelebA\train",],
    r"../checkpoints/datasets/places2_val.flist"  : [r"E:\DeepLearningData\EdgeConnect\CelebA\eval",],
    r"../checkpoints/datasets/places2_test.flist" : [r"E:\DeepLearningData\EdgeConnect\CelebA\test",],
    r"../checkpoints/datasets/masks_train.flist"  : [r"E:\DeepLearningData\EdgeConnect\mask\CustomMask3\train",],
    r"../checkpoints/datasets/masks_val.flist"    : [r"E:\DeepLearningData\EdgeConnect\mask\CustomMask3\eval",],
    r"../checkpoints/datasets/masks_test.flist"   : [r"E:\DeepLearningData\EdgeConnect\mask\CustomMask3\test",],
}

for flist_path, dataset_paths in flist_dataset_paths.items():
    print('creating', flist_path)
    images = []

    # auto create directory
    os.makedirs(os.path.dirname(flist_path), exist_ok=True)

    # find all image
    for dataset_path in dataset_paths:
        for root, dirs, files in os.walk(dataset_path):
            print('loading : ' + root)
            for file in files:
                # print('image : ' + file)
                if os.path.splitext(file)[1].upper() in ext:
                    images.append(os.path.join(root, file))

    images = sorted(images)
    np.savetxt(flist_path, images, fmt='%s')