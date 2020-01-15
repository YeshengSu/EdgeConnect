import os
from collections import defaultdict

import numpy as np
from PIL import Image
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtWidgets import QWidget, QPushButton, QTreeWidget, QTreeWidgetItem, QLabel, QHBoxLayout, QGridLayout, \
    QFileDialog, QMessageBox


class FileExplorer(QWidget):
    PREVIEW_WIDTH = 450

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

        ft1 = QFont()
        ft1.setPointSize(15)
        self.image_preview = QLabel('No Info')
        self.image_preview.setFont(ft1)
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setWordWrap(True)

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
            preview_height = int(self.PREVIEW_WIDTH * self.image_data.shape[0] / self.image_data.shape[1])
            resized_img_data = np.array(Image.fromarray(self.image_data).resize((self.PREVIEW_WIDTH, preview_height), Image.HAMMING))
            height, width, bytesPerComponent = resized_img_data.shape
            QImg = QImage(resized_img_data, width, height, width*3, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(QImg)
            self.image_preview.setPixmap(pixmap)
            self.parent.clip_area.set_image(self.image_data)

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