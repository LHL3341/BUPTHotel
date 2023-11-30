import sys
import os 
sys.path.append(os.path.abspath('.'))
print(os.path.abspath('.'))
os.chdir(os.path.abspath('./Client/'))
print(os.path.abspath('.'))
from entity import *

from PyQt5.QtWidgets import QApplication, QListWidgetItem
from MainWindow import MainUi
from LoginWindow import LoginUi
from UserSelectWindow import UserSelectUi
from UserControlWindow import UserControlUi
from Manager_Air_Window import ManagerAirUi
from Manager_Bill_Window import ManagerBillUi
from PyQt5 import QtCore,QtNetwork
from PyQt5.QtCore import QTimer
import requests
import json


SERVERADDR = 'http://127.0.0.1:10086'
FREQ = 600

# 利用一个控制器来控制页面的跳转
class Controller:
    def __init__(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_panel)
        self.room_options = {
            1: ['101', '102', '103', '104', '105', '106', '107', '108', '109', '110'],
            2: ['201', '202', '203', '204', '205', '206', '207', '208', '209', '210'],
            3: ['301', '302', '303', '304', '305', '306', '307', '308', '309', '310'],
            4: ['401', '402', '403', '404', '405', '406', '407', '408', '409', '410']
        }
        self.main = MainUi()
        self.main.pushButton_user.clicked.connect(self.show_userselect)
        self.main.pushButton_manager.clicked.connect(self.show_login)

        self.login = LoginUi()
        self.login.pushButton_login.clicked.connect(self.log_in)
        self.login.pushButton_return.clicked.connect(self.show_main)

        self.userselect = UserSelectUi()
        self.userselect.pushButton_return.clicked.connect(self.show_main)
        self.userselect.comboBox_floor.currentIndexChanged.connect(self.select)
        self.userselect.pushButton_ok.clicked.connect(self.show_usercontrol)

        self.usercontrol = UserControlUi()
        self.usercontrol.pushButton_return.clicked.connect(self.show_main)
        self.usercontrol.status_changed.connect(self.remote_control)

        self.manager_air = ManagerAirUi()
        self.manager_air.pushButton_return.clicked.connect(self.show_main)

        self.manager_bill = ManagerBillUi()
        self.manager_bill.pushButton_return.clicked.connect(self.show_main)
        self.manager_bill.comboBox_floor.currentIndexChanged.connect(self.change_list)


    # 跳转到 hello 窗口
    def show_main(self):
        self.login.close()
        self.userselect.close()
        self.usercontrol.close()
        self.manager_air.close()
        self.manager_bill.close()
        self.main.show()

    def show_userselect(self):
        self.main.close()
        # 初始化选择页面
        self.userselect = UserSelectUi()
        self.userselect.pushButton_return.clicked.connect(self.show_main)
        self.userselect.comboBox_floor.addItems(["点击选择楼层", "1楼", "2楼", "3楼", "4楼"])
        self.userselect.comboBox_floor.currentIndexChanged.connect(self.select)
        self.userselect.show()

    def show_usercontrol(self):
        self.timer.start(FREQ)
        floor = self.userselect.comboBox_floor.currentText()
        room = self.userselect.comboBox_room.currentText()
        if floor[0] =='点'or room[0] == '点':
            return
        response = requests.post(SERVERADDR+f'/check_in?room_id={room[:3]}',json={"guest_name":1})
        if json.loads(response.text)['status'] == "success!":
            self.floor = int(floor[0])
            self.room = room[:3]
            self.usercontrol.roomid = self.room
            self.userselect.close()
            self.usercontrol.show()

    # 跳转到 login 窗口
    def show_login(self):
        self.main.close()
        # 格式化登录界面
        self.login = LoginUi()
        self.login.pushButton_login.clicked.connect(self.log_in)
        self.login.pushButton_return.clicked.connect(self.show_main)
        self.login.show()

    def show_manager_air(self):
        self.login.close()
        self.manager_air.stackedWidget.setCurrentIndex(0)
        self.manager_air.pushButton_5.clicked.connect(self.central_control)
        self.manager_air.show()

    def show_manager_bill(self):
        self.login.close()
        self.manager_bill.stackedWidget.setCurrentIndex(0)
        self.manager_bill.listWidget_room.clear()
        self.manager_bill.comboBox_floor.setCurrentIndex(0)
        self.manager_bill.show()

    def log_in(self):
        if self.login.lineEdit_name.text() == "1" and self.login.lineEdit_password.text() == "123":
            self.show_manager_air()

        elif self.login.lineEdit_name.text() == "2" and self.login.lineEdit_password.text() == "123":
            self.show_manager_bill()

        else:
            self.login.label_error.setText("用户名或密码错误....请重试")
            self.login.lineEdit_name.clear()
            self.login.lineEdit_password.clear()

    def select(self, index):
        self.userselect.comboBox_room.clear()
        # 获取对应的房间号选项

        self.userselect.comboBox_room.addItem('点击选择房间号')
        room_options = self.room_options.get(index, [])
        self.userselect.comboBox_room.addItems(room_options)
        self.userselect.comboBox_room.setCurrentIndex(0)
        self.userselect.pushButton_ok.clicked.connect(self.show_usercontrol)


    def change_list(self, index):

        self.manager_bill.listWidget_room.clear()
        room_options = self.room_options.get(index, [])

        self.manager_bill.listWidget_room.addItems(room_options)

    def remote_control(self,device_id,option):
        """
        开关 0
        风速 1
        温度升 2
        温度降 3
        """
        panel = self.usercontrol
        time = datetime.now()
        response = requests.get(SERVERADDR +f'/get_device_status?device_id={device_id}')
        response = json.loads(response.text)
        past_state = DeviceStatus(**response)
        speed = {'low':0,'mid':1,'high':2}

        if (not past_state.working) and option != 0:
            return
        if option == 0:
            past_state.working = (past_state.working+1)%2
            if past_state.working:
                response = requests.post(SERVERADDR +f'/remote_control?device_id={device_id}',json={"command":'turn_on',"args":[]})
            else:
                response = requests.post(SERVERADDR +f'/remote_control?device_id={device_id}',json={"command":'turn_off',"args":[]})
        elif option ==1:
            if past_state.speed == 'low':
                past_state.speed = 'mid'
            elif past_state.speed == 'mid':
                past_state.speed = 'high'    
            elif past_state.speed == 'high':
                past_state.speed = 'low'

            response = requests.post(SERVERADDR +f'/remote_control?device_id={device_id}',json={"command":'set_speed',"args":past_state.speed})
        elif option == 2:
            past_state.target_temperature +=1
            response = requests.post(SERVERADDR +f'/remote_control?device_id={device_id}',json={"command":'set_temperature',"args":past_state.target_temperature})
        elif option == 3:
            past_state.target_temperature -=1
            response = requests.post(SERVERADDR +f'/remote_control?device_id={device_id}',json={"command":'set_temperature',"args":past_state.target_temperature})

        panel.isopen = past_state.working
        panel.current_speed = past_state.speed
        panel.target_temp = past_state.target_temperature
        panel.current_temp = past_state.env_temperature
        self.usercontrol.update_screen.emit()
        
    def central_control(self):
        #TODO：非法输入检测
        window = self.manager_air
        
        limit = [int(window.lineEdit_min.text()),int(window.lineEdit_max.text())]
        cost = [float(window.lineEdit_low.text()),float(window.lineEdit_middle.text()),float(window.lineEdit_high.text())]
        requests.post(SERVERADDR+'/admin_control',json={"command":'set_valid_range',"args":limit})
        requests.post(SERVERADDR+'/admin_control',json={"command":'set_mode',"args":1})
        requests.post(SERVERADDR+'/admin_control',json={"command":'turn_on',"args":[]})
        requests.post(SERVERADDR+'/admin_control',json={"command":'turn_off',"args":[]})
        requests.post(SERVERADDR+'/admin_control',json={"command":'set_price',"args":cost})

    def update_panel(self):
        panel = self.usercontrol
        time = datetime.now()
        response = requests.get(SERVERADDR +f'/get_device_status?device_id={panel.roomid}')
        response = json.loads(response.text)
        past_state = DeviceStatus(**response)
        panel.isopen = past_state.working
        panel.current_speed = past_state.speed
        panel.target_temp = past_state.target_temperature
        panel.current_temp = past_state.env_temperature
        self.usercontrol.update_screen.emit()

    def get_log(self):
        # 前台打印详单，调用/log/{room_id}接口
        #roomid = 
        #response = requests.get(SERVERADDR+'/log/{room_id}')
        #print(response.text)
        #res = json.loads(response.text)
        pass

    def get_bill(self):
        # 前台打印账单，调用@app.get('/cost/{room_id}')接口（接口需要自己实现）
        pass

    def check_out(self):
        # 前台退房，调用服务器@app.post('/{room_id}/check_out')接口
        #response = requests.post(SERVERADDR+f'/{room_id}/check_out')
        pass

    def get_room_status(self):
        # 前台查看房间状态，例如
        #response = requests.get(SERVERADDR+'/state/rooms/101')
        #res = json.loads(response.text)获取该房间状态
        #然后将其显示到前端
        pass

    def monitor(self):
        # 空调管理员监控各空调状态，前端界面需要一目了然
        # 用@app.get('/state/rooms')接口获取空调状态
        pass

if __name__ == '__main__':
    try:
        response = requests.get(SERVERADDR)
        print(response.text)
        
        response = requests.get(SERVERADDR+'/get_all_device_status')
        print(response.text)
        response = requests.get(SERVERADDR+'/get_device_status?device_id=101')
        print(response.text)
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
        app = QApplication(sys.argv)
        controller = Controller()
        controller.show_main()
        controller1 = Controller()
        controller1.show_main()
        controller2 = Controller()
        controller2.show_main()
        controller3 = Controller()
        controller3.show_main()
        controller4 = Controller()
        controller4.show_main()
        sys.exit(app.exec_())

    except Exception as e:
        print('未连接到服务器')
        print(e)
    
    
