import math
import numpy as np
from PIL import Image
from PyQt5.QtCore import Qt, QRect, QStringListModel
from PyQt5.QtGui import QFont, QPalette, QColor, QImage, QPixmap, QPainter, QPen
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton, QColorDialog, QSpinBox, QGridLayout, QListView, \
    QAbstractItemView


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
        self.image_clip_data = None
        self.show_image_size = (0, 0)
        self.image_mask_data = None
        self.image_draw_data = None
        self.item_name_to_clip_image_info = {}  # (clip image, clip_pos_size, left_up_pos, size)
        self.item_name_to_mask_image_info = {}  # (mask image)
        self.current_item_name = 'image 1'
        self.color_pen = QColor(50, 200, 50)
        self.brush_size = 6

        # pick color
        ft2 = QFont()
        ft2.setBold(True)
        self.btn_color = QPushButton('Color', self)
        self.btn_color.clicked.connect(self.on_clicked_color)
        self.btn_color.setFont(ft2)
        pla = self.btn_color.palette()
        pla.setColor(QPalette.ButtonText, self.color_pen)
        self.btn_color.setPalette(pla)

        # brush setting
        self.label_brush_size = QLabel('Brush Size')
        self.spin_brush_size = QSpinBox(self)
        self.spin_brush_size.setRange(2, 50)
        self.spin_brush_size.setSingleStep(1)
        self.spin_brush_size.setValue(self.brush_size)
        self.spin_brush_size.valueChanged.connect(self.on_change_brush_size)

        self.btn_clear = QPushButton('Clear Mask', self)
        self.btn_clear.clicked.connect(self.on_clicked_clear)
        self.btn_finish = QPushButton('Finish', self)
        self.btn_finish.clicked.connect(self.on_clicked_finish)

        # image
        self.image_draw_mask = DrawLabel('image draw', self)
        self.image_draw_mask.setAlignment(Qt.AlignTop)
        self.image_draw_mask.setCursor(Qt.CrossCursor)
        self.image_mask_preview = QLabel('mask preview')
        self.image_mask_preview.setAlignment(Qt.AlignHCenter)

        # listview
        self.label_listview = QLabel('Select Image')
        self.model_image_clip = QStringListModel(self)
        self.model_image_clip.setStringList(self.item_name_to_clip_image_info.keys())
        self.listview_image_clip = QListView(self)
        self.listview_image_clip.setModel(self.model_image_clip)
        self.listview_image_clip.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listview_image_clip.doubleClicked.connect(lambda: self.on_clicked_listview_item(self.listview_image_clip))

        self.grid_layout = QGridLayout()
        self.grid_layout.addWidget(self.label_brush_size,   0, 0, 1, 1)
        self.grid_layout.addWidget(self.spin_brush_size, 0, 1, 1, 1)
        self.grid_layout.addWidget(self.btn_color, 0, 2, 1, 1)
        self.grid_layout.addWidget(self.btn_clear, 0, 6, 1, 2)
        self.grid_layout.addWidget(self.btn_finish, 0, 8, 1, 2)
        self.grid_layout.addWidget(self.image_draw_mask, 1, 0, 5, 5)
        self.grid_layout.addWidget(self.image_mask_preview, 1, 5, 5, 5, Qt.AlignTop)
        self.grid_layout.addWidget(self.label_listview, 6, 5, 1, 2)
        self.grid_layout.addWidget(self.listview_image_clip, 7, 5, 1, 4)
        self.setLayout(self.grid_layout)

    def set_image(self, item_name_to_clip_image_info):
        self.item_name_to_clip_image_info = item_name_to_clip_image_info
        self.model_image_clip.setStringList(self.item_name_to_clip_image_info.keys())

        for item_name, clip_image_info in self.item_name_to_clip_image_info.items():
            self.item_name_to_mask_image_info[item_name] = (np.copy(clip_image_info[0]),)
            self.item_name_to_mask_image_info[item_name][0][:, :] = 0

        self.parent.setTabEnabled(2, True)

        self.set_current_draw('image 1')

    def set_current_draw(self, item_name):
        from image_inpainting_demo import set_label_image
        self.current_item_name = item_name

        # show preview
        self.image_clip_data = self.item_name_to_clip_image_info[self.current_item_name][0]

        # create mask
        self.image_mask_data = self.item_name_to_mask_image_info[self.current_item_name][0]
        set_label_image(self.image_mask_preview, self.PREVIEW_MASK_WIDTH, self.image_mask_data)

        # draw image
        color = (self.color_pen.red(), self.color_pen.green(), self.color_pen.blue())
        self.image_draw_data = np.copy((self.image_mask_data / 255 * color) + ((1 - self.image_mask_data / 255) * self.image_clip_data))
        self.image_draw_data = np.array(self.image_draw_data, np.uint8)
        self.show_image_size = set_label_image(self.image_draw_mask, self.PREVIEW_CLIP_WIDTH, self.image_draw_data)

    def draw_mask(self, pos):
        from image_inpainting_demo import set_label_image

        show_width, show_height = self.show_image_size
        height, width, bytesPerComponent = self.image_clip_data.shape

        # calculate row coordinate
        to_row_width, to_row_height = width / float(show_width), height / float(show_height)
        actual_x, actual_y = int(pos[0] * to_row_width), int(pos[1] * to_row_height)

        half_size = int(math.ceil(self.brush_size / 2.0))
        x1, y1 = min(actual_x + half_size, width), min(actual_y + half_size, width)
        x0, y0 = max(actual_x - (self.brush_size - half_size), 0), max(actual_y - (self.brush_size - half_size), 0)

        self.image_mask_data[y0:y1 + 1, x0:x1 + 1] = 255
        set_label_image(self.image_mask_preview, self.PREVIEW_MASK_WIDTH, self.image_mask_data)
        self.refresh_mask_image((x0,y0,x1,y1))

    def refresh_mask_image(self, x0y0_x1y1=None):
        from image_inpainting_demo import set_label_image

        color = (self.color_pen.red(), self.color_pen.green(), self.color_pen.blue())
        if x0y0_x1y1:
            x1, y1 = x0y0_x1y1[2], x0y0_x1y1[3]
            x0, y0 = x0y0_x1y1[0], x0y0_x1y1[1]
            self.image_draw_data[y0:y1 + 1, x0:x1 + 1] = color
        else:
            self.image_draw_data = np.copy((self.image_mask_data / 255 * color) + ((1 - self.image_mask_data / 255) * self.image_clip_data))
            self.image_draw_data = np.array(self.image_draw_data, np.uint8)
        set_label_image(self.image_draw_mask, self.PREVIEW_CLIP_WIDTH, self.image_draw_data)

    def on_clicked_color(self):
        new_color = QColorDialog.getColor()
        if new_color.isValid():
            pla = self.btn_color.palette()
            pla.setColor(QPalette.ButtonText, new_color)
            self.btn_color.setPalette(pla)
            self.color_pen = new_color
            self.refresh_mask_image()

    def on_change_brush_size(self):
        self.brush_size = int(self.spin_brush_size.value())

    def on_clicked_clear(self):
        from image_inpainting_demo import set_label_image

        self.image_mask_data[:, :] = 0
        set_label_image(self.image_mask_preview, self.PREVIEW_MASK_WIDTH, self.image_mask_data)
        self.refresh_mask_image()

    def on_clicked_finish(self):
        self.parent.image_inpainting.set_image(self.item_name_to_clip_image_info, self.item_name_to_mask_image_info)

    def on_clicked_listview_item(self, listview):
        data = listview.currentIndex().data()
        self.set_current_draw(data)