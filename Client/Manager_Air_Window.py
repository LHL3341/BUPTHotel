from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
Ui_Manager_Air, ManagerAirBase = uic.loadUiType("./ui/manager_air.ui")


class ManagerAirUi(QWidget, Ui_Manager_Air):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.pushButton_central.clicked.connect(self.display1)
        self.pushButton_branch.clicked.connect(self.display2)
        self.mainswitch = False

    def display1(self):
        self.stackedWidget.setCurrentIndex(0)

    def display2(self):
        self.stackedWidget.setCurrentIndex(1)

    '''备用
    def change_page1(self, index):
        self.stackedWidget_2.setCurrentIndex(index)
    
    def change_page2(self, item):
        # 获取点击的项的索引
        index = self.listWidget.row(item)
        # 切换到对应的页面
        self.stackedWidget_3.setCurrentIndex(index + 1)
    '''