from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
Ui_Login, LoginBase = uic.loadUiType("./ui/login.ui")


class LoginUi(QWidget, Ui_Login):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        #self.login.pushButton_login.clicked.connect(self.log_in)
        self.use_background()

    def use_background(self):
        # 创建 QLabel 以显示背景图像
        background_label = QLabel(self)
        pixmap = QPixmap("images/background.jpg")
        background_label.setPixmap(pixmap)
        background_label.setGeometry(0, 0, pixmap.width(), pixmap.height())
        background_label.lower()  # 将其置于底层
