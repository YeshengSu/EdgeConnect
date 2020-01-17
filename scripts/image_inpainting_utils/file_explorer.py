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
        self.folder_to_filename = defaultdict(list)
        self.item_clicked = None
        self.item_selected_image = None
        self.image_selected_data = None

        self.button_add_folder = QPushButton('Add Folder', self)
        self.button_add_folder.clicked.connect(self.on_clicked_add_folder)
        self.button_remove_folder = QPushButton('Remove Folder', self)
        self.button_remove_folder.clicked.connect(self.on_clicked_remove_folder)

        self.widget_tree = QTreeWidget(self)
        self.widget_tree.setColumnCount(2)
        self.widget_tree.setHeaderLabels(['Files', 'Format'])
        self.widget_tree.setColumnWidth(0, 350)
        # self.tree.setMaximumWidth(500)
        self.widget_tree.itemClicked.connect(self.on_clicked_tree_item)

        self.item_preview = QTreeWidgetItem(self.widget_tree)
        self.item_preview.setText(0, 'ALL Folders')

        ft1 = QFont()
        ft1.setPointSize(15)
        self.label_image_preview = QLabel('No Info')
        self.label_image_preview.setFont(ft1)
        self.label_image_preview.setAlignment(Qt.AlignCenter)
        self.label_image_preview.setWordWrap(True)

        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.button_add_folder)
        self.hbox_layout.addWidget(self.button_remove_folder)
        self.grid_layout = QGridLayout()
        self.grid_layout.addLayout(self.hbox_layout, 0, 0, 1, 1)
        self.grid_layout.addWidget(self.widget_tree, 1, 0, 5, 5)
        self.grid_layout.addWidget(self.label_image_preview, 1, 5, 5, 5)
        self.setLayout(self.grid_layout)

        self.widget_tree.expandAll()

    def on_clicked_tree_item(self, item, column):
        from image_inpainting_demo import set_label_image

        self.label_image_preview.setText(item.text(column))
        self.item_clicked = item

        # is select image
        if item.checkState(0) == Qt.Checked:
            if self.item_selected_image and self.item_selected_image is not item:
                self.item_selected_image.setCheckState(0, Qt.Unchecked)
            self.item_selected_image = item
            self.item_selected_image.setCheckState(0, Qt.Checked)

            image_path = self.item_selected_image.parent().text(0) + '/' + self.item_selected_image.text(0)
            print('select image path : ', image_path)
            # preview image
            new_img = Image.open(image_path)
            new_img = new_img.convert('RGB')
            self.image_selected_data = np.asarray(new_img)
            set_label_image(self.label_image_preview, self.PREVIEW_WIDTH, self.image_selected_data)
            self.parent.clip_area.set_image(self.image_selected_data)

    def on_clicked_add_folder(self):
        self.new_folder_path = QFileDialog.getExistingDirectory(self, "Add Folder", self.new_folder_path)
        if self.new_folder_path:
            if self.new_folder_path in self.folder_to_filename:
                QMessageBox.warning(self, 'warning', 'New folder has exist !')
                return

            print('add new folder path : ', self.new_folder_path)

            # add folder item
            folder_item = QTreeWidgetItem(self.item_preview)
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
            self.folder_to_filename[self.new_folder_path] = images

            # add image item
            for i, image in enumerate(images):
                item = QTreeWidgetItem(folder_item)
                item.setText(0, image)
                item.setText(1, 'Image')
                item.setCheckState(0, Qt.Unchecked)

    def on_clicked_remove_folder(self):
        if self.item_clicked:
            if self.item_clicked.text(1) == 'Folder':
                if self.item_clicked.text(0) in self.folder_to_filename:
                    if self.item_selected_image:
                        self.item_selected_image.setCheckState(0, Qt.Unchecked)
                    del self.folder_to_filename[self.item_clicked.text(0)]
                    self.item_preview.removeChild(self.item_clicked)
                    self.item_clicked = None
                    self.item_selected_image = None
                    self.parent.setTabEnabled(1, False)
                    self.parent.setTabEnabled(2, False)
                    self.parent.setTabEnabled(3, False)
            else:
                QMessageBox.warning(self, 'warning', 'only allow to remove folder !')
