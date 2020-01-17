import numpy as np

from PIL import Image
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QImage, QPixmap, QFont, QPen, QColor, QPalette, QPainter
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QGridLayout, QColorDialog


class ClipableLabel(QLabel):
    def __init__(self, str, parent=None):
        super(ClipableLabel, self).__init__(str, parent=parent)
        self.parent = parent
        self.x0 = 0
        self.y0 = 0
        self.x1 = 0
        self.y1 = 0
        self.flag = False

    def mousePressEvent(self, event):
        self.flag = True
        self.x0 = event.x()
        self.y0 = event.y()
        # restrict to image area
        max_size = self.parent.show_image_size
        self.x0 = max(min(max_size[0], self.x0), 0)
        self.y0 = max(min(max_size[1], self.y0), 0)

    def mouseReleaseEvent(self, event):
        self.flag = False
        max_side = min(abs(self.x1 - self.x0), abs(self.y1 - self.y0))
        self.parent.set_area((self.x0, self.y0), (max_side, max_side))

    def mouseMoveEvent(self, event):
        if self.flag:
            self.x1 = event.x()
            self.y1 = event.y()
            # restrict to image area
            max_size = self.parent.show_image_size
            self.x1 = max(min(max_size[0], self.x1), 0)
            self.y1 = max(min(max_size[1], self.y1), 0)
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        max_side = min(abs(self.x1 - self.x0), abs(self.y1 - self.y0))
        rect = QRect(self.x0, self.y0, max_side, max_side)
        painter = QPainter(self)
        painter.setPen(QPen(self.parent.pen_color, 2, Qt.SolidLine))
        painter.drawRect(rect)

    def reset(self):
        self.x0 = 0
        self.y0 = 0
        self.x1 = 0
        self.y1 = 0
        self.flag = False
        self.update()


class ClipArea(QWidget):
    PREVIEW_SHOW_WIDTH = 450
    PREVIEW_CLIP_WIDTH = 300

    def __init__(self, parent=None):
        super(ClipArea, self).__init__(parent=parent)
        self.parent = parent
        self.show_image_data = None
        self.show_image_size = (0, 0)
        self.clip_image_data = None
        self.clip_pos_size = (0, 0, 0, 0)
        self.pen_color = QColor(50, 200, 50)

        # text tips
        ft1 = QFont()
        ft1.setPointSize(15)
        self.label_clip = QLabel('image clip')
        self.label_clip.setFont(ft1)
        self.label_preview = QLabel('clip area preview')
        self.label_preview.setFont(ft1)

        # pick color
        ft2 = QFont()
        ft2.setBold(True)
        self.color_btn = QPushButton('Color', self)
        self.color_btn.clicked.connect(self.on_clicked_color)
        self.color_btn.setFont(ft2)
        pla = self.color_btn.palette()
        pla.setColor(QPalette.ButtonText, self.pen_color)
        self.color_btn.setPalette(pla)

        # image
        self.image_to_clip = ClipableLabel('image clip', self)
        self.image_to_clip.setAlignment(Qt.AlignTop)
        self.image_to_clip.setCursor(Qt.CrossCursor)
        self.clip_area_preview = QLabel('clip area preview')
        self.clip_area_preview.setAlignment(Qt.AlignHCenter)

        self.grid_layout = QGridLayout()
        self.grid_layout.addWidget(self.color_btn, 0, 0, 1, 1)
        self.grid_layout.addWidget(self.label_clip, 1, 0, 1, 5, Qt.AlignHCenter)
        self.grid_layout.addWidget(self.label_preview, 1, 5, 1, 5, Qt.AlignHCenter)
        self.grid_layout.addWidget(self.image_to_clip, 2, 0, 10, 5)
        self.grid_layout.addWidget(self.clip_area_preview, 2, 5, 10, 5, Qt.AlignTop)

        self.setLayout(self.grid_layout)

    def set_image(self, image_data):
        from image_inpainting_demo import set_label_image
        self.show_image_data = image_data
        self.show_image_size = set_label_image(self.image_to_clip, self.PREVIEW_SHOW_WIDTH, self.show_image_data)
        self.image_to_clip.reset()
        self.parent.setTabEnabled(1, True)
        self.parent.setTabEnabled(2, False)
        self.parent.setTabEnabled(3, False)

    def set_area(self, left_up_pos, size):
        from image_inpainting_demo import set_label_image

        show_width, show_height = self.show_image_size
        height, width, bytesPerComponent = self.show_image_data.shape

        # calculate row coordinate
        to_row_width, to_row_height = width / float(show_width), height / float(show_height)
        actual_x, actual_y = int(left_up_pos[0] * to_row_width), int(left_up_pos[1] * to_row_height)
        actual_width, actual_height = int(size[0] * to_row_width), int(size[1] * to_row_height)
        if not actual_width or not actual_height:
            return

        # clip image
        self.clip_pos_size = (actual_x, actual_y, actual_width, actual_height)
        row_image = Image.fromarray(self.show_image_data)
        cp_image = row_image.crop((actual_x, actual_y, actual_x + actual_width, actual_y + actual_height))
        self.clip_image_data = np.asarray(cp_image)

        # preview
        set_label_image(self.clip_area_preview, self.PREVIEW_CLIP_WIDTH, self.clip_image_data)

        # pass image data to draw mask
        self.parent.draw_mask.set_image(self.clip_image_data)

    def on_clicked_color(self):
        new_color = QColorDialog.getColor()
        if new_color.isValid():
            pla = self.color_btn.palette()
            pla.setColor(QPalette.ButtonText, new_color)
            self.color_btn.setPalette(pla)
            self.pen_color = new_color
