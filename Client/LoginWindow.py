from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
Ui_Login, LoginBase = uic.loadUiType("./ui/login.ui")


class LoginUi(QWidget, Ui_Login):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        #self.login.pushButton_login.clicked.connect(self.log_in)

