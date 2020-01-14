import os
import sys
import numpy as np
from collections import defaultdict

from PIL import Image
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QImage, QPixmap, QFont
from PyQt5.QtWidgets import QApplication, QWidget, QTreeWidget, QTreeWidgetItem, QLabel, QHBoxLayout, QToolBox, \
    QToolButton, QGroupBox, QVBoxLayout, QTabWidget, QPushButton, QGridLayout, QFileDialog, QMessageBox, QScrollArea, \
    QScrollBar

import utils

class FileExplorer(QWidget):
    preview_width = 450

    def __init__(self, parent=None):
        super(FileExplorer, self).__init__(parent=parent)
        self.parent = parent

        self.new_folder_path = ''
        self.all_folders = defaultdict(list)
        self.click_item = None
        self.select_image = None
        self.image_data = None

        self.button_add_folder = QPushButton('Add Folder', self)
        self.button_add_folder.clicked.connect(self.on_clicked_add_folder)
        self.button_remove_folder = QPushButton('Remove Folder', self)
        self.button_remove_folder.clicked.connect(self.on_clicked_remove_folder)

        self.tree = QTreeWidget(self)
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(['Files', 'Format'])
        self.tree.setColumnWidth(0, 350)
        # self.tree.setMaximumWidth(500)
        self.tree.itemClicked.connect(self.on_clicked_tree_item)

        self.preview = QTreeWidgetItem(self.tree)
        self.preview.setText(0, 'ALL Folders')

        self.image_preview = QLabel('No Info')
        self.image_preview.setAlignment(Qt.AlignCenter)

        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.button_add_folder)
        self.hbox_layout.addWidget(self.button_remove_folder)
        self.grid_layout = QGridLayout()
        self.grid_layout.addLayout(self.hbox_layout, 0, 0, 1, 1)
        self.grid_layout.addWidget(self.tree, 1, 0, 5, 5)
        self.grid_layout.addWidget(self.image_preview, 1, 5, 5, 5)
        self.setLayout(self.grid_layout)

        self.tree.expandAll()

    def on_clicked_tree_item(self, item, column):
        self.image_preview.setText(item.text(column))
        self.click_item = item

        # is select image
        if item.checkState(0) == Qt.Checked:
            if self.select_image and self.select_image is not item:
                self.select_image.setCheckState(0, Qt.Unchecked)
            self.select_image = item
            self.select_image.setCheckState(0, Qt.Checked)

            image_path = self.select_image.parent().text(0) + '/' + self.select_image.text(0)
            print('select image path : ', image_path)
            # preview image
            new_img = Image.open(image_path)
            new_img = new_img.convert('RGB')
            self.image_data = np.asarray(new_img)
            preview_height = int(self.preview_width * self.image_data.shape[0] / self.image_data.shape[1])
            resized_img_data = np.array(Image.fromarray(self.image_data).resize((self.preview_width, preview_height), Image.HAMMING))
            height, width, bytesPerComponent = resized_img_data.shape
            QImg = QImage(resized_img_data, width, height, width*3, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(QImg)
            self.image_preview.setPixmap(pixmap)
            self.parent.select_area.select_image(self.image_data)

    def on_clicked_add_folder(self):
        self.new_folder_path = QFileDialog.getExistingDirectory(self, "Add Folder", self.new_folder_path)
        if self.new_folder_path:
            if self.new_folder_path in self.all_folders:
                QMessageBox.warning(self, 'warning', 'New folder has exist !')
                return

            print('add new folder path : ', self.new_folder_path)

            # add folder item
            folder_item = QTreeWidgetItem(self.preview)
            folder_item.setText(0, self.new_folder_path)
            folder_item.setText(1, 'Folder')

            images = os.listdir(self.new_folder_path)

            # filter images
            def is_image(path):
                suffix = path.split('.')[-1]
                if suffix in ('jpg', 'png', 'bmp', 'jpeg'):
                    return True
                return False

            images = list(filter(is_image, images))
            images.sort()
            self.all_folders[self.new_folder_path] = images

            # add image item
            for i, image in enumerate(images):
                item = QTreeWidgetItem(folder_item)
                item.setText(0, image)
                item.setText(1, 'Image')
                item.setCheckState(0, Qt.Unchecked)

    def on_clicked_remove_folder(self):
        if self.click_item:
            if self.click_item.text(1) == 'Folder':
                if self.click_item.text(0) in self.all_folders:
                    if self.select_image:
                        self.select_image.setCheckState(0, Qt.Unchecked)
                    del self.all_folders[self.click_item.text(0)]
                    self.preview.removeChild(self.click_item)
                    self.click_item = None
                    self.select_image = None
                    self.parent.setTabEnabled(1, False)
                    self.parent.setTabEnabled(2, False)
                    self.parent.setTabEnabled(3, False)
            else:
                QMessageBox.warning(self, 'warning', 'only allow to remove folder !')


class SelectArea(QWidget):
    preview_width = 450

    def __init__(self, parent=None):
        super(SelectArea, self).__init__(parent=parent)
        self.parent = parent
        self.image_data = None

        self.ft = QFont()
        self.ft.setPointSize(25)
        self.label_select = QLabel('image show')
        self.label_select.setAlignment(Qt.AlignCenter)
        self.label_select.setFont(self.ft)
        self.label_preview = QLabel('selected area preview')
        self.label_preview.setAlignment(Qt.AlignCenter)
        self.label_preview.setFont(self.ft)

        self.image_select = QLabel('image show')
        self.image_select.setAlignment(Qt.AlignCenter)
        self.image_select.setCursor(Qt.CrossCursor)
        self.selected_area_preview = QLabel('image select')
        self.selected_area_preview.setAlignment(Qt.AlignCenter)

        self.grid_layout = QGridLayout()
        self.grid_layout.addWidget(self.label_select, 0, 2, 1, 1)
        self.grid_layout.addWidget(self.label_preview, 0, 7, 1, 1)
        self.grid_layout.addWidget(self.image_select, 1, 0, 5, 5)
        self.grid_layout.addWidget(self.selected_area_preview, 1, 5, 5, 5)

        self.setLayout(self.grid_layout)

    def select_image(self, image_data):
        self.image_data = image_data
        preview_height = int(self.preview_width * self.image_data.shape[0] / self.image_data.shape[1])
        resized_img_data = np.array(Image.fromarray(self.image_data).resize((self.preview_width, preview_height), Image.HAMMING))
        height, width, bytesPerComponent = resized_img_data.shape
        QImg = QImage(resized_img_data, width, height, width * 3, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(QImg)
        self.image_select.setPixmap(pixmap)
        self.selected_area_preview.setPixmap(pixmap)

        self.parent.setTabEnabled(1, True)

class DrawMask(QWidget):
    def __init__(self, parent=None):
        super(DrawMask, self).__init__(parent=parent)
        self.label = QLabel('DrawMask')
        self.h_layout = QHBoxLayout()
        self.h_layout.addWidget(self.label)
        self.setLayout(self.h_layout)


class ImageInpainting(QWidget):
    def __init__(self, parent=None):
        super(ImageInpainting, self).__init__(parent=parent)
        self.label = QLabel('ImageInpainting')
        self.h_layout = QHBoxLayout()
        self.h_layout.addWidget(self.label)
        self.setLayout(self.h_layout)


class MainWindow(QTabWidget):
    # my_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)

        self.file_explorer = FileExplorer(self)
        self.select_area = SelectArea(self)
        self.draw_mask = DrawMask(self)
        self.image_inpainting = ImageInpainting(self)

        self.setWindowTitle('Edge Connect')
        self.resize(1000, 800)
        self.addTab(self.file_explorer, 'File Explorer')
        self.addTab(self.select_area, 'Select Area')
        self.addTab(self.draw_mask, 'Draw Mask')
        self.addTab(self.image_inpainting, 'Image Inpainting')

        self.setTabEnabled(1, False)
        self.setTabEnabled(2, False)
        self.setTabEnabled(3, False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = MainWindow()
    demo.show()
    sys.exit(app.exec_())
