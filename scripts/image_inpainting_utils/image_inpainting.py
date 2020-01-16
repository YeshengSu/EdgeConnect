from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout


class ImageInpainting(QWidget):
    def __init__(self, parent=None):
        super(ImageInpainting, self).__init__(parent=parent)
        self.parent = parent
        self.label = QLabel('ImageInpainting')
        self.h_layout = QHBoxLayout()
        self.h_layout.addWidget(self.label)
        self.setLayout(self.h_layout)

    def set_image(self, image_data):
        self.parent.setTabEnabled(3, True)
        return