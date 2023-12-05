import sys
from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
Ui_Main, MainBase = uic.loadUiType("./ui/main.ui")


class MainUi(QWidget, Ui_Main):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton_quit.clicked.connect(self.sys_exit)
        self.use_background()

    def sys_exit(self):
        sys.exit()

    def use_background(self):
        # 创建 QLabel 以显示背景图像
        background_label = QLabel(self)
        pixmap = QPixmap("images/background.jpg")
        background_label.setPixmap(pixmap)
        background_label.setGeometry(0, 0, pixmap.width(), pixmap.height())
        background_label.lower()  # 将其置于底层