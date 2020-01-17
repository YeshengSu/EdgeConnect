import math
import numpy as np
from PIL import Image
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QFont, QPalette, QColor, QImage, QPixmap, QPainter, QPen
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton, QColorDialog, QSpinBox, QGridLayout


class DrawLabel(QLabel):
    def __init__(self, str, parent=None):
        super(DrawLabel, self).__init__(str, parent=parent)
        self.parent = parent
        self.x0 = 0
        self.y0 = 0

    def mousePressEvent(self, event):
        self.x0 = event.x()
        self.y0 = event.y()
        # restrict to image area
        max_size = self.parent.show_image_size
        if 0 <= self.x0 <= max_size[0] and 0 <= self.y0 <= max_size[1]:
            self.parent.draw_mask((self.x0, self.y0))

    def mouseMoveEvent(self, event):
        self.x0 = event.x()
        self.y0 = event.y()
        # restrict to image area
        max_size = self.parent.show_image_size
        if 0 <= self.x0 <= max_size[0] and 0 <= self.y0 <= max_size[1]:
            self.parent.draw_mask((self.x0, self.y0))


class DrawMask(QWidget):
    PREVIEW_CLIP_WIDTH = 450
    PREVIEW_MASK_WIDTH = 450

    def __init__(self, parent=None):
        super(DrawMask, self).__init__(parent=parent)
        self.parent = parent
        self.clip_image_data = None
        self.show_image_size = (0, 0)
        self.mask_image_data = None
        self.draw_image_data = None
        self.pen_color = QColor(50, 200, 50)
        self.brush_size = 6

        # pick color
        ft2 = QFont()
        ft2.setBold(True)
        self.color_btn = QPushButton('Color', self)
        self.color_btn.clicked.connect(self.on_clicked_color)
        self.color_btn.setFont(ft2)
        pla = self.color_btn.palette()
        pla.setColor(QPalette.ButtonText, self.pen_color)
        self.color_btn.setPalette(pla)

        # brush setting
        self.label_brush_size = QLabel('Brush Size')
        self.select_brush_size = QSpinBox(self)
        self.select_brush_size.setRange(2, 50)
        self.select_brush_size.setSingleStep(1)
        self.select_brush_size.setValue(self.brush_size)
        self.select_brush_size.valueChanged.connect(self.on_change_brush_size)

        self.clear_btn = QPushButton('Clear Mask', self)
        self.clear_btn.clicked.connect(self.on_clicked_clear)
        self.finish_btn = QPushButton('Finish', self)
        self.finish_btn.clicked.connect(self.on_clicked_finish)

        # image
        self.image_to_mask = DrawLabel('image clip', self)
        self.image_to_mask.setAlignment(Qt.AlignTop)
        self.image_to_mask.setCursor(Qt.CrossCursor)
        self.mask_area_preview = QLabel('clip area preview')
        self.mask_area_preview.setAlignment(Qt.AlignHCenter)

        self.grid_layout = QGridLayout()
        self.grid_layout.addWidget(self.label_brush_size,   0, 0, 1, 1)
        self.grid_layout.addWidget(self.select_brush_size,  0, 1, 1, 1)
        self.grid_layout.addWidget(self.color_btn,          0, 2, 1, 1)
        self.grid_layout.addWidget(self.clear_btn,          0, 6, 1, 2)
        self.grid_layout.addWidget(self.finish_btn,         0, 8, 1, 2)
        self.grid_layout.addWidget(self.image_to_mask,      1, 0, 5, 5)
        self.grid_layout.addWidget(self.mask_area_preview,  1, 5, 5, 5, Qt.AlignTop)
        self.setLayout(self.grid_layout)

    def set_image(self, image_data):
        from image_inpainting_demo import set_label_image

        self.clip_image_data = image_data
        # show preview
        self.show_image_size = set_label_image(self.image_to_mask, self.PREVIEW_CLIP_WIDTH, self.clip_image_data)

        # draw image
        self.draw_image_data = np.copy(self.clip_image_data)

        # create mask
        self.mask_image_data = np.copy(self.clip_image_data)
        self.mask_image_data[:, :] = 0
        set_label_image(self.mask_area_preview, self.PREVIEW_MASK_WIDTH, self.mask_image_data)

        self.parent.setTabEnabled(2, True)

    def draw_mask(self, pos):
        from image_inpainting_demo import set_label_image

        show_width, show_height = self.show_image_size
        height, width, bytesPerComponent = self.clip_image_data.shape

        # calculate row coordinate
        to_row_width, to_row_height = width / float(show_width), height / float(show_height)
        actual_x, actual_y = int(pos[0] * to_row_width), int(pos[1] * to_row_height)

        half_size = int(math.ceil(self.brush_size / 2.0))
        x1, y1 = min(actual_x + half_size, width), min(actual_y + half_size, width)
        x0, y0 = max(actual_x - (self.brush_size - half_size), 0), max(actual_y - (self.brush_size - half_size), 0)

        self.mask_image_data[y0:y1 + 1, x0:x1 + 1] = 255
        set_label_image(self.mask_area_preview, self.PREVIEW_MASK_WIDTH, self.mask_image_data)
        self.refresh_mask_image((x0,y0,x1,y1))

        # print('draw _x:{}, _y:{}'.format(actual_x, actual_y))

    def refresh_mask_image(self, x0y0_x1y1=None):
        from image_inpainting_demo import set_label_image

        color = (self.pen_color.red(), self.pen_color.green(), self.pen_color.blue())
        if x0y0_x1y1:
            x1, y1 = x0y0_x1y1[2], x0y0_x1y1[3]
            x0, y0 = x0y0_x1y1[0], x0y0_x1y1[1]
            self.draw_image_data[y0:y1 + 1, x0:x1 + 1] = color
        else:
            self.draw_image_data = np.copy((self.mask_image_data/255 * color) + ((1 - self.mask_image_data/255) * self.clip_image_data))
            self.draw_image_data = np.array(self.draw_image_data, np.uint8)
        set_label_image(self.image_to_mask, self.PREVIEW_CLIP_WIDTH, self.draw_image_data)

    def on_clicked_color(self):
        new_color = QColorDialog.getColor()
        if new_color.isValid():
            pla = self.color_btn.palette()
            pla.setColor(QPalette.ButtonText, new_color)
            self.color_btn.setPalette(pla)
            self.pen_color = new_color
            self.refresh_mask_image()

    def on_change_brush_size(self):
        self.brush_size = int(self.select_brush_size.value())

    def on_clicked_clear(self):
        from image_inpainting_demo import set_label_image

        self.mask_image_data[:, :] = 0
        set_label_image(self.mask_area_preview, self.PREVIEW_MASK_WIDTH, self.mask_image_data)
        self.refresh_mask_image()

    def on_clicked_finish(self):
        self.parent.image_inpainting.set_image(self.mask_image_data)
