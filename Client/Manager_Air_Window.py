from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem

Ui_Manager_Air, ManagerAirBase = uic.loadUiType("./ui/manager_air.ui")


class ManagerAirUi(QWidget, Ui_Manager_Air):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.pushButton_central.clicked.connect(self.display1)
        self.pushButton_branch.clicked.connect(self.display2)
        self.tableWidget.setRowCount(40)
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels(['Room', 'Power', 'Mode',
                                                    'Env-temp','Target-temp','Speed','Totalcost'])
        self.tableWidget.setEditTriggers(self.tableWidget.NoEditTriggers)
        
        self.mainswitch = False
        
        
    def display1(self):
        self.stackedWidget.setCurrentIndex(0)

    def display2(self):
        self.stackedWidget.setCurrentIndex(1)

    def addItem(self,res):
        for i in range(40):
            room_status=res[i]
            self.tableWidget.setItem(i,0, QTableWidgetItem(res[i]["room_id"]))
            if res[i]["working"]:
                s="开"
            else:
                s="关"

            self.tableWidget.setItem(i,1, QTableWidgetItem(s))
            self.tableWidget.setItem(i,2, QTableWidgetItem(str(res[i]["mode"])))
            self.tableWidget.setItem(i,3, QTableWidgetItem(str(res[i]["env_temperature"])))
            self.tableWidget.setItem(i,4, QTableWidgetItem(str(res[i]["target_temperature"])))
            self.tableWidget.setItem(i,5, QTableWidgetItem(res[i]["speed"]))
            self.tableWidget.setItem(i,6, QTableWidgetItem(str(res[i]["total_cost"])))
            #if res[i]["wind_speed"]==0:
            #    w="低"
            #elif res[i]["wind_speed"]==1:
            #    w="中"
            #elif res[i]["wind_speed"]==2:
            #    w="高"
            #self.tableWidget.setItem(i,7, QTableWidgetItem(w))
            #self.tableWidget.setItem(i,8, QTableWidgetItem(str(res[i]["totalcost"])))
            self.tableWidget.resizeColumnsToContents()
            self.tableWidget.resizeRowsToContents()

    '''备用
    def change_page1(self, index):
        self.stackedWidget_2.setCurrentIndex(index)
    
    def change_page2(self, item):
        # 获取点击的项的索引
        index = self.listWidget.row(item)
        # 切换到对应的页面
        self.stackedWidget_3.setCurrentIndex(index + 1)
    '''