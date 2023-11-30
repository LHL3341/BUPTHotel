from PyQt5.QtWidgets import QWidget
from PyQt5 import uic,QtCore
Ui_UserSelect, UserSelectBase = uic.loadUiType("./ui/userselect.ui")


class UserSelectUi(QWidget, Ui_UserSelect):
    signal = QtCore.pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        

    def reserve_room(self):
        floor = self.comboBox_floor.currentText()
        room = self.comboBox_room.currentText()
        

