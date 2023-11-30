from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
Ui_Manager_Bill, ManagerBillBase = uic.loadUiType("./ui/manager_bill.ui")


class ManagerBillUi(QWidget, Ui_Manager_Bill):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.pushButton_report.clicked.connect(self.display1)
        self.pushButton_checkinout.clicked.connect(self.display2)

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

