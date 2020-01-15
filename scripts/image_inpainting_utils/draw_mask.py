import numpy as np
from PIL import Image
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QFont, QPalette, QColor, QImage, QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton, QColorDialog, QSpinBox, QGridLayout


class DrawMask(QWidget):
    PREVIEW_CLIP_WIDTH = 450
    PREVIEW_MASK_WIDTH = 450

    def __init__(self, parent=None):
        super(DrawMask, self).__init__(parent=parent)
        self.parent = parent
        self.clip_image_data = None
        self.show_image_size = (0, 0)
        self.pen_color = QColor(50, 200, 50)

        # pick color
        ft2 = QFont()
        ft2.setBold(True)
        self.color_btn = QPushButton('Pick Pen Color', self)
        self.color_btn.clicked.connect(self.on_clicked_color)
        self.color_btn.setFont(ft2)
        pla = self.color_btn.palette()
        pla.setColor(QPalette.ButtonText, self.pen_color)
        self.color_btn.setPalette(pla)

        # brush setting
        self.label_brush_size = QLabel('Brush Size')
        self.select_brush_size = QSpinBox(self)
        self.select_brush_size.setRange(2, 20)
        self.select_brush_size.setSingleStep(1)
        self.select_brush_size.setValue(6)
        self.select_brush_size.valueChanged.connect(self.on_change_brush_size)

        self.clear_btn = QPushButton('Clear Mask', self)
        self.clear_btn.clicked.connect(self.on_clicked_clear)

        # image
        self.image_to_mask = QLabel('image clip')
        self.image_to_mask.setAlignment(Qt.AlignTop)
        self.image_to_mask.setCursor(Qt.CrossCursor)
        self.mask_area_preview = QLabel('clip area preview')
        self.mask_area_preview.setAlignment(Qt.AlignHCenter)

        self.grid_layout = QGridLayout()
        self.grid_layout.addWidget(self.label_brush_size, 0, 0, 1, 1)
        self.grid_layout.addWidget(self.select_brush_size, 0, 1, 1, 1)
        self.grid_layout.addWidget(self.color_btn, 0, 2, 1, 1)
        self.grid_layout.addWidget(self.clear_btn, 0, 4, 1, 2)
        self.grid_layout.addWidget(self.image_to_mask, 1, 0, 10, 5)
        self.grid_layout.addWidget(self.mask_area_preview, 1, 10, 5, 5, Qt.AlignTop)
        self.setLayout(self.grid_layout)

    def set_image(self, image_data):
        self.clip_image_data = image_data

        preview_height = int(self.PREVIEW_CLIP_WIDTH * self.clip_image_data.shape[0] / self.clip_image_data.shape[1])
        resized_img_data = np.array(
                Image.fromarray(self.clip_image_data).resize((self.PREVIEW_CLIP_WIDTH, preview_height), Image.HAMMING))
        height, width, bytesPerComponent = resized_img_data.shape
        self.show_image_size = (width, height)
        QImg = QImage(resized_img_data, width, height, width * 3, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(QImg)
        self.image_to_mask.setPixmap(pixmap)
        self.mask_area_preview.setPixmap(pixmap)

        self.parent.setTabEnabled(2, True)

    def on_clicked_color(self):
        new_color = QColorDialog.getColor()
        if new_color.isValid():
            pla = self.color_btn.palette()
            pla.setColor(QPalette.ButtonText, new_color)
            self.color_btn.setPalette(pla)
            self.pen_color = new_color

    def on_change_brush_size(self):
        print(self.select_brush_size.value())

    def on_clicked_clear(self):
        print('clear')
