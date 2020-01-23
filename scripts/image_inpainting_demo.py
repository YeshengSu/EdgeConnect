import sys
import numpy as np
from PIL import Image
from PyQt5.QtGui import QPalette, QColor, QImage, QPixmap
from PyQt5.QtWidgets import QTabWidget, QApplication

from image_inpainting_utils.draw_mask import DrawMask
from image_inpainting_utils.file_explorer import FileExplorer
from image_inpainting_utils.image_inpainting import ImageInpainting
from image_inpainting_utils.clip_area import ClipArea


def set_label_image(label, preview_width, ori_data):
    preview_height = int(preview_width * ori_data.shape[0] / ori_data.shape[1])
    image = Image.fromarray(ori_data).resize((preview_width, preview_height), Image.HAMMING)
    resized_img_data = np.asarray(image.convert('RGB'))
    height, width, bytesPerComponent = resized_img_data.shape
    QImg = QImage(resized_img_data, width, height, width * 3, QImage.Format_RGB888)
    pixmap = QPixmap.fromImage(QImg)
    label.setPixmap(pixmap)
    return (width, height)


class MainWindow(QTabWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)

        self.file_explorer = FileExplorer(self)
        self.clip_area = ClipArea(self)
        self.draw_mask = DrawMask(self)
        self.image_inpainting = ImageInpainting(self)

        self.resize(1000, 800)
        self.setMinimumSize(1000, 800)
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
