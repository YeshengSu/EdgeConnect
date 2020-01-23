import cv2
from PyQt5.QtCore import Qt, QThread
import glob
import os
import random

import math
import numpy as np
import torch
import torchvision.transforms.functional as F
from PIL import Image
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QGridLayout, QVBoxLayout
from imageio import imread
from skimage.color import rgb2gray, gray2rgb
from skimage.feature import canny
from torch.utils.data import DataLoader

import utils



class ImageDataset(torch.utils.data.Dataset):
    def __init__(self, config, data, edge_data, mask_data, augment=True, training=True):
        super(ImageDataset, self).__init__()
        self.mode = config.MODE
        self.augment = augment
        self.training = training
        self.data = data  # 最好为n^2 的不带alpha的RGB图片
        self.edge_data = edge_data
        self.mask_data = mask_data  # 必须位图 类型为 Pil的 ‘1’

        self.input_size = config.INPUT_SIZE
        self.max_power_2 = config.MAX_POWER_2
        self.sigma = config.SIGMA
        self.edge = config.EDGE
        self.mask = config.MASK
        self.nms = config.NMS

        # in test mode, there's a one-to-one relationship between mask and image
        # masks are loaded non random
        if config.MODE == 2:
            self.mask = 6

        # preventing inaccurate ratio of img in train and losing details in test
        self.is_center_crop = True if self.mode == 1 else False

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        try:
            item = self.load_item(index)
        except:
            print('loading error: index : {}'.format([index]))
            item = self.load_item(0)

        return item

    def load_item(self, index):
        size = self.input_size

        # load image
        ori_img = self.data[index]

        # gray to rgb
        if len(ori_img.shape) < 3:
            ori_img = gray2rgb(ori_img)

        # resize/crop if needed
        if size != 0:
            img = utils.resize(ori_img, size, size, self.is_center_crop)
        else:
            max_size = max(ori_img.shape[0], ori_img.shape[1])
            max_size = 2 ** min(math.ceil(math.log2(max_size)), self.max_power_2)
            img = utils.resize(ori_img, max_size, max_size, self.is_center_crop)

        # create grayscale image
        img_gray = rgb2gray(img)

        # load mask
        mask = self.load_mask(img, index)

        # resize/crop if needed
        if size == 0:
            img_shape = img.shape
            mask = utils.resize(mask, img_shape[0], img_shape[1], self.is_center_crop)

        # load edge
        edge = self.load_edge(img_gray, index, mask)

        # augment data
        if self.augment and np.random.binomial(1, 0.5) > 0:
            img = img[:, ::-1, ...]
            img_gray = img_gray[:, ::-1, ...]
            edge = edge[:, ::-1, ...]
            mask = mask[:, ::-1, ...]

        return list(ori_img.shape), self.to_tensor(img), self.to_tensor(img_gray), self.to_tensor(edge), self.to_tensor(mask)

    def load_edge(self, img, index, mask):
        sigma = self.sigma

        # in test mode images are masked (with masked regions),
        # using 'mask' parameter prevents canny to detect edges for the masked regions
        mask = None if self.training else (1 - mask / 255).astype(np.bool)

        # canny
        if self.edge == 1:
            # no edge
            if sigma == -1:
                return np.zeros(img.shape).astype(np.float)

            # random sigma
            if sigma == 0:
                sigma = random.randint(1, 4)

            return canny(img, sigma=sigma, mask=mask).astype(np.float)

        # external
        else:
            imgh, imgw = img.shape[0:2]
            edge = self.edge_data[index]
            edge = utils.resize(edge, imgh, imgw, self.is_center_crop)

            # non-max suppression
            if self.nms == 1:
                edge = edge * canny(img, sigma=sigma, mask=mask)

            return edge

    def load_mask(self, img, index):
        imgh, imgw = img.shape[0:2]
        mask_type = self.mask

        # external + random block
        if mask_type == 4:
            mask_type = 1 if np.random.binomial(1, 0.5) == 1 else 3

        # external + random block + half
        elif mask_type == 5:
            mask_type = np.random.randint(1, 4)

        # random block
        if mask_type == 1:
            return utils.create_mask(imgw, imgh, imgw // 2, imgh // 2)

        # half
        if mask_type == 2:
            # randomly choose right or left
            return utils.create_mask(imgw, imgh, imgw // 2, imgh, 0 if random.random() < 0.5 else imgw // 2, 0)

        # external
        if mask_type == 3:
            mask_index = random.randint(0, len(self.mask_data) - 1)
            mask = self.mask_data[mask_index]
            mask = utils.resize(mask, imgh, imgw, self.is_center_crop)
            mask = (mask > 0).astype(np.uint8) * 255       # threshold due to interpolation
            return mask

        # test mode: load mask non random
        if mask_type == 6:
            mask = self.mask_data[index%len(self.mask_data)]
            mask = utils.resize(mask, imgh, imgw, centerCrop=False)
            mask = rgb2gray(mask)
            mask = (mask > 0).astype(np.uint8) * 255
            return mask

    def to_tensor(self, img):
        img = Image.fromarray(img)
        img_t = F.to_tensor(img).float()
        return img_t

    def create_iterator(self, batch_size):
        while True:
            sample_loader = DataLoader(
                dataset=self,
                batch_size=batch_size,
                drop_last=True
            )

            for item in sample_loader:
                yield item


class InpaintingThread(QThread):
    def __init__(self, parent):
        super(InpaintingThread, self).__init__(parent)
        self.parent = parent

    def run(self):
        self.parent.image_inpainting()

class ImageInpainting(QWidget):
    PREVIEW_CLIP_WIDTH = 200
    PREVIEW_MASK_WIDTH = 200
    PREVIEW_CLIP_MASK_WIDTH = 200
    PREVIEW_EDGE_WIDTH = 200
    PREVIEW_RESULT_WIDTH = 450

    INFO_READY = 'Info : READY'
    INFO_PROCESS = 'Info : Processing......'
    INFO_FINSH = 'Info : ACCOMPLISHMENT !'

    def __init__(self, parent=None):
        super(ImageInpainting, self).__init__(parent=parent)
        self.parent = parent
        self.image_clip_data = None
        self.image_mask_data = None
        self.image_clip_mask_data = None
        self.image_edge_data = None
        self.image_result_data = None
        self.edge_model = None
        self.inpaint_model = None
        self.config = None

        self.btn_start = QPushButton('Start Process !', self)
        self.btn_start.clicked.connect(self.on_clicked_start)
        self.btn_show = QPushButton('Show Final Image !', self)
        self.btn_show.clicked.connect(self.on_clicked_show)

        self.thread_inpainting = InpaintingThread(self)

        # label
        ft1, ft2 = QFont(), QFont()
        ft1.setPointSize(15)
        ft2.setPointSize(20)
        self.label_clip = QLabel('Origin image')
        self.label_mask = QLabel('Mask image')
        self.label_clip_mask = QLabel('Origin image with mask')
        self.label_edge = QLabel('generated edge image')
        self.label_result = QLabel('Result')
        self.label_result.setFont(ft1)
        self.label_info = QLabel(self.INFO_READY)
        self.label_info.setFont(ft2)

        # image
        self.label_image_clip = QLabel('image clip')
        self.label_image_mask = QLabel('image mask')
        self.label_image_clip_mask = QLabel('image clip mask')
        self.label_image_edge = QLabel('image edge')
        self.label_image_result = QLabel('image mask')

        self.vbox_layout1 = QVBoxLayout()
        self.vbox_layout1.addWidget(self.label_clip, alignment=Qt.AlignBottom)
        self.vbox_layout1.addWidget(self.label_image_clip)
        self.vbox_layout1.addWidget(self.label_mask, alignment=Qt.AlignBottom)
        self.vbox_layout1.addWidget(self.label_image_mask)
        self.vbox_layout2 = QVBoxLayout()
        self.vbox_layout2.addWidget(self.label_clip_mask, alignment=Qt.AlignBottom)
        self.vbox_layout2.addWidget(self.label_image_clip_mask)
        self.vbox_layout2.addWidget(self.label_edge, alignment=Qt.AlignBottom)
        self.vbox_layout2.addWidget(self.label_image_edge)

        self.vbox_layout3 = QVBoxLayout()
        self.vbox_layout3.addWidget(self.label_result)
        self.vbox_layout3.addWidget(self.label_image_result)
        self.vbox_layout3.addWidget(self.label_info)

        self.grid_layout = QGridLayout()
        self.grid_layout.addWidget(self.btn_start, 0, 0, 1, 3)
        self.grid_layout.addWidget(self.btn_show, 0, 4, 1, 3)
        self.grid_layout.addLayout(self.vbox_layout1, 1, 0, 8, 3)
        self.grid_layout.addLayout(self.vbox_layout2, 1, 3, 8, 3)
        self.grid_layout.addLayout(self.vbox_layout3, 1, 6, 9, 9, Qt.AlignCenter)
        self.setLayout(self.grid_layout)

    def set_image(self, image_clip_data, image_mask_data):
        from image_inpainting_demo import set_label_image

        # clip image
        self.image_clip_data = image_clip_data
        set_label_image(self.label_image_clip, self.PREVIEW_CLIP_WIDTH, self.image_clip_data)

        # mask image
        self.image_mask_data = image_mask_data
        set_label_image(self.label_image_mask, self.PREVIEW_MASK_WIDTH, self.image_mask_data)

        # clip mask image
        color = (255, 255, 255)
        self.image_clip_mask_data = np.copy((self.image_mask_data / 255 * color) + ((1 - self.image_mask_data / 255) * self.image_clip_data))
        self.image_clip_mask_data = np.array(self.image_clip_mask_data, np.uint8)
        set_label_image(self.label_image_clip_mask, self.PREVIEW_CLIP_MASK_WIDTH, self.image_clip_mask_data)

        # edge image
        self.image_edge_data = np.copy(self.image_clip_mask_data)
        set_label_image(self.label_image_edge, self.PREVIEW_EDGE_WIDTH, self.image_edge_data)

        # result image
        self.image_result_data = np.zeros(self.image_clip_mask_data.shape, np.uint8)
        set_label_image(self.label_image_result, self.PREVIEW_RESULT_WIDTH, self.image_result_data)

        self.parent.setTabEnabled(3, True)
        self.label_info.setText(self.INFO_READY)
        return

    def on_clicked_start(self):
        print('on_click_start')
        self.btn_start.setEnabled(False)
        self.btn_show.setEnabled(False)
        self.parent.setTabEnabled(0, False)
        self.parent.setTabEnabled(1, False)
        self.parent.setTabEnabled(2, False)
        self.label_info.setText(self.INFO_PROCESS)
        self.thread_inpainting.start()

    def on_clicked_show(self):
        row_image_data = np.copy(self.parent.file_explorer.image_selected_data)
        paste_pos_size = self.parent.clip_area.clip_pos_size
        x, y, width, height = paste_pos_size

        row_img = Image.fromarray(row_image_data)
        result_img = Image.fromarray(self.image_result_data)
        row_img.paste(result_img, (x, y, x + width, y + height))
        row_img.show('inpainted image')

    def image_inpainting(self):
        from image_inpainting_demo import set_label_image
        from main import load_config
        from src.models import EdgeModel
        from src.models import InpaintingModel

        mode = 2  # test

        if not self.config:
            self.config = load_config(mode, '.././checkpoints')  # start test

        # cuda visble devices
        os.environ['CUDA_VISIBLE_DEVICES'] = ','.join(str(e) for e in self.config.GPU)

        # init device
        if torch.cuda.is_available():
            self.config.DEVICE = torch.device("cuda")
            torch.backends.cudnn.benchmark = True  # cudnn auto-tuner
        else:
            self.config.DEVICE = torch.device("cpu")

        # set cv2 running threads to 1 (prevents deadlocks with pytorch dataloader)
        cv2.setNumThreads(0)

        # initialize random seed
        torch.manual_seed(self.config.SEED)
        torch.cuda.manual_seed_all(self.config.SEED)
        np.random.seed(self.config.SEED)
        random.seed(self.config.SEED)

        if not self.edge_model and not self.inpaint_model:
            model_name = 'edge_inpaint'
            self.edge_model = EdgeModel(self.config).to(self.config.DEVICE)
            self.inpaint_model = InpaintingModel(self.config).to(self.config.DEVICE)
            # load model
            self.edge_model.load()
            self.inpaint_model.load()
            # init edge connect
            self.edge_model.eval()
            self.inpaint_model.eval()

        # load dataset
        test_dataset = ImageDataset(self.config, [self.image_clip_data], [], [self.image_mask_data],
                                    augment=False, training=False)

        # start testing
        print('\nstart testing...\n')


        test_loader = DataLoader(dataset=test_dataset, batch_size=1)

        def to_cuda(*args):
            return (item.to(self.config.DEVICE) if hasattr(item, 'to') else item for item in args)

        for items in test_loader:
            ori_shapes, images, images_gray, edges, masks = to_cuda(*items)
            edges = self.edge_model(images_gray, edges, masks).detach()
            outputs = self.inpaint_model(images, edges, masks)
            outputs_merged = (outputs * masks) + (images * (1 - masks))

            # output edge img
            image_edge_data = self._get_image_data_from_tensor(edges, ori_shapes)
            self.image_edge_data = image_edge_data
            set_label_image(self.label_image_edge, self.PREVIEW_EDGE_WIDTH, self.image_edge_data)

            # output result img
            image_result_data = self._get_image_data_from_tensor(outputs_merged, ori_shapes)
            self.image_result_data = image_result_data
            set_label_image(self.label_image_result, self.PREVIEW_RESULT_WIDTH, self.image_result_data)

            break
        print('\nEnd test....')

        self.btn_start.setEnabled(True)
        self.btn_show.setEnabled(True)
        self.parent.setTabEnabled(0, True)
        self.parent.setTabEnabled(1, True)
        self.parent.setTabEnabled(2, True)
        self.label_info.setText(self.INFO_FINSH)

    def _get_image_data_from_tensor(self, gpu_data, ori_shapes):
        # postprocess
        outputs_merged = gpu_data * 255.0
        outputs_merged = outputs_merged.permute(0, 2, 3, 1)
        output = outputs_merged.int()
        output = output[0]

        # output result img
        ori_shapes = [t.item() for t in ori_shapes]
        image = output.cpu().numpy().astype(np.uint8)
        image = image.squeeze()
        image_data = utils.resize(image, ori_shapes[0], ori_shapes[1], False)

        return image_data