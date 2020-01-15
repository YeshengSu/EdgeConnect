import sys

from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QTabWidget, QApplication

from image_inpainting_utils.draw_mask import DrawMask
from image_inpainting_utils.file_explorer import FileExplorer
from image_inpainting_utils.image_inpainting import ImageInpainting
from image_inpainting_utils.clip_area import ClipArea


class MainWindow(QTabWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)

        self.file_explorer = FileExplorer(self)
        self.clip_area = ClipArea(self)
        self.draw_mask = DrawMask(self)
        self.image_inpainting = ImageInpainting(self)

        self.resize(1000, 800)
        self.setWindowTitle('Edge Connect')

        self.addTab(self.file_explorer, 'File Explorer')
        self.addTab(self.clip_area, 'Select Area')
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