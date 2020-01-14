from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout


class DrawMask(QWidget):
    def __init__(self, parent=None):
        super(DrawMask, self).__init__(parent=parent)
        self.label = QLabel('DrawMask')
        self.h_layout = QHBoxLayout()
        self.h_layout.addWidget(self.label)
        self.setLayout(self.h_layout)