import sys
from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
Ui_Main, MainBase = uic.loadUiType("./ui/main.ui")


class MainUi(QWidget, Ui_Main):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton_quit.clicked.connect(self.sys_exit)

    def sys_exit(self):
        sys.exit()
