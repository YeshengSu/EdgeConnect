import math
import numpy as np
from PIL import Image
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton, QGridLayout, QVBoxLayout


class ImageInpainting(QWidget):
    PREVIEW_CLIP_WIDTH = 200
    PREVIEW_MASK_WIDTH = 200
    PREVIEW_CLIP_MASK_WIDTH = 200
    PREVIEW_RESULT_WIDTH = 450

    def __init__(self, parent=None):
        super(ImageInpainting, self).__init__(parent=parent)
        self.parent = parent
        self.image_clip_data = None
        self.image_mask_data = None
        self.image_clip_mask_data = None
        self.image_result_data = None

        self.btn_finish = QPushButton('Start Process !', self)
        self.btn_finish.clicked.connect(self.on_clicked_start)
        self.btn_show = QPushButton('Show Final Image !', self)
        self.btn_show.clicked.connect(self.on_clicked_show)

        # label
        ft1 = QFont()
        ft1.setPointSize(15)
        self.label_clip = QLabel('Origin image')
        self.label_mask = QLabel('Mask image')
        self.label_clip_mask = QLabel('Origin image with mask')
        self.label_result = QLabel('Result')
        self.label_result.setFont(ft1)

        # image
        self.label_image_clip = QLabel('image clip')
        self.label_image_mask = QLabel('image mask')
        self.label_image_clip_mask = QLabel('image clip mask')
        self.label_image_result = QLabel('image mask')

        self.vbox_layout1 = QVBoxLayout()
        self.vbox_layout1.addWidget(self.label_clip)
        self.vbox_layout1.addWidget(self.label_image_clip)
        self.vbox_layout1.addWidget(self.label_mask)
        self.vbox_layout1.addWidget(self.label_image_mask)
        self.vbox_layout1.addWidget(self.label_clip_mask)
        self.vbox_layout1.addWidget(self.label_image_clip_mask)

        self.vbox_layout2 = QVBoxLayout()
        self.vbox_layout2.addWidget(self.label_result)
        self.vbox_layout2.addWidget(self.label_image_result)

        self.grid_layout = QGridLayout()
        self.grid_layout.addWidget(self.btn_finish, 0, 0, 1, 3)
        self.grid_layout.addWidget(self.btn_show, 0, 4, 1, 3)
        self.grid_layout.addLayout(self.vbox_layout1, 1, 0, 9, 3)
        self.grid_layout.addLayout(self.vbox_layout2, 1, 6, 9, 9, Qt.AlignCenter)
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

        # result image
        self.image_result_data = np.copy(self.image_clip_mask_data)
        set_label_image(self.label_image_result, self.PREVIEW_RESULT_WIDTH, self.image_result_data)

        self.parent.setTabEnabled(3, True)
        return

    def on_clicked_start(self):
        print('on_click_start')

    def on_clicked_show(self):
        row_image_data = np.copy(self.parent.file_explorer.image_selected_data)
        paste_pos_size = self.parent.clip_area.clip_pos_size
        x, y, width, height = paste_pos_size

        row_img = Image.fromarray(row_image_data)
        result_img = Image.fromarray(self.image_result_data)
        row_img.paste(result_img, (x, y, x + width, y + height))
        row_img.show('inpainted image')
