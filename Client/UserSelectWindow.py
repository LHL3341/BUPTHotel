from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QPixmap
Ui_UserSelect, UserSelectBase = uic.loadUiType("./ui/userselect.ui")


class UserSelectUi(QWidget, Ui_UserSelect):
    signal = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.frame.setStyleSheet("border-radius: 15px;")
        # self.comboBox_floor.setStyleSheet("QComboBox QAbstractItemView { color: white; }")
        # self.comboBox_room.setStyleSheet("QComboBox QAbstractItemView { color: white; }")
        self.use_background()

    def reserve_room(self):
        floor = self.comboBox_floor.currentText()
        room = self.comboBox_room.currentText()

    def use_background(self):
        # 创建 QLabel 以显示背景图像
        background_label = QLabel(self)
        pixmap = QPixmap("images/background.jpg")
        background_label.setPixmap(pixmap)
        background_label.setGeometry(0, 0, pixmap.width(), pixmap.height())
        background_label.lower()  # 将其置于底层
