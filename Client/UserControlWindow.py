from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import pyqtSignal
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
Ui_UserControl, UserControlBase = uic.loadUiType("./ui/usercontrol.ui")


class UserControlUi(QWidget, Ui_UserControl):
    status_changed = pyqtSignal(str, int)
    update_screen = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.roomid = ''
        self.isopen = 0
        self.cost = 0
        self.current_mode = 'warm'
        self.current_speed = ''
        self.current_temp = 18
        self.target_temp = 24
        
        self.lcdNumber.display(0)
        self.pushButton_onoff.clicked.connect(self.change)
        self.pushButton_up.clicked.connect(self.up_temp)
        self.pushButton_down.clicked.connect(self.down_temp)
        self.pushButton_speed.clicked.connect(self.change_speed)
        self.update_screen.connect(self.update)

        self.use_background()

    def change(self):
        self.status_changed.emit(self.roomid,0)

    # 定义槽函数，使 LCDNumber 值增加
    def up_temp(self): 
        self.status_changed.emit(self.roomid,2)

    # 定义槽函数，使 LCDNumber 值减少
    def down_temp(self):
        self.status_changed.emit(self.roomid,3)


    def change_speed(self):

        self.status_changed.emit(self.roomid,1)

        
    def update(self):
        if self.isopen:
            #self.lcdNumber.display(self.current_temp)
            #if self.current_speed == 0:
            #    self.label_speed.setText("Low")
            #elif self.current_speed == 1:
            #    self.label_speed.setText("Medium")
            #else:
            #    self.label_speed.setText("High")
            self.label_speed.setText(self.current_speed)
            self.label_mode.setText(self.current_mode)
            
            self.pushButton_onoff.setText("OFF")

        else:
            #self.lcdNumber.display(0)
            #self.label_mode.setText("")
            self.label_speed.setText("")
            self.pushButton_onoff.setText("ON")
        self.label_cost.setText(str(round(self.cost,2)))
        self.label_envtmp.setText(f"{self.current_temp}")
        self.lcdNumber.display(self.target_temp)

    def use_background(self):
        # 创建 QLabel 以显示背景图像
        background_label = QLabel(self)
        pixmap = QPixmap("images/background.jpg")
        background_label.setPixmap(pixmap)
        background_label.setGeometry(0, 0, pixmap.width(), pixmap.height())
        background_label.lower()  # 将其置于底层