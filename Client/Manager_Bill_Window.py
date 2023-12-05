from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5 import uic, QtWidgets
from PyQt5.QtGui import QPixmap
Ui_Manager_Bill, ManagerBillBase = uic.loadUiType("./ui/manager_bill.ui")


class ManagerBillUi(QWidget, Ui_Manager_Bill):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.pushButton_report.clicked.connect(self.display1)
        self.pushButton_checkinout.clicked.connect(self.display2)
        self.use_background()
        self.tableWidget_status.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.tableWidget_status.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
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

    def use_background(self):
        # 创建 QLabel 以显示背景图像
        background_label = QLabel(self)
        pixmap = QPixmap("images/background.jpg")
        background_label.setPixmap(pixmap)
        background_label.setGeometry(0, 0, pixmap.width(), pixmap.height())
        background_label.lower()  # 将其置于底层
