import sys
import os 
sys.path.append(os.path.abspath('.'))
print(os.path.abspath('.'))
os.chdir(os.path.abspath('./Client/'))
print(os.path.abspath('.'))
from entity import *

from PyQt5.QtWidgets import QApplication, QTableWidgetItem
from MainWindow import MainUi
from LoginWindow import LoginUi
from UserSelectWindow import UserSelectUi
from UserControlWindow import UserControlUi
from Manager_Air_Window import ManagerAirUi
from Manager_Bill_Window import ManagerBillUi
from PyQt5 import QtCore,QtNetwork
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
import requests
import openpyxl
import json
import re

SERVERADDR = 'http://127.0.0.1:10086'
FREQ = 600

# 利用一个控制器来控制页面的跳转
class Controller:
    def __init__(self,username):
        self.username = username
        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_event)
        self.room_options = {
            1: ['101(109c)', '102(109c2)', '103(113f)', '104(112b)', '105(112g)', '106', '107', '108', '109', '110'],
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
        self.manager_bill.listWidget_room.itemClicked.connect(self.get_room_status)
        self.manager_bill.pushButton_checkout.clicked.connect(self.check_out)
        self.manager_bill.comboBox_floor.currentIndexChanged.connect(self.change_list)
        self.manager_bill.pushButton_printdetail.clicked.connect(self.get_log)
        self.manager_bill.pushButton_printbill.clicked.connect(self.get_bill)



    # 跳转到 hello 窗口
    def show_main(self):
        self.login.close()
        self.userselect.close()
        self.usercontrol.close()
        self.manager_air.close()
        self.manager_bill.close()
        self.main.show()
        self.main.setWindowTitle(self.username)


    def show_userselect(self):
        self.main.close()
        # 初始化选择页面
        self.userselect = UserSelectUi()
        self.userselect.pushButton_return.clicked.connect(self.show_main)
        self.userselect.comboBox_floor.addItems(["Click to select the floor", "1st", "2nd", "3rd", "4th"])
        self.userselect.comboBox_floor.currentIndexChanged.connect(self.select)
        self.userselect.setWindowTitle(self.username)
        self.userselect.show()


    def show_usercontrol(self):
        self.timer.start(FREQ)
        self.usercontrol.label_name.setText(f"Welcome,{self.username}!")
        floor = self.userselect.comboBox_floor.currentText()
        room = self.userselect.comboBox_room.currentText()
        if floor[0] =='点'or room[0] == '点':
            return
        self.floor = int(floor[0])
        self.room = room[:3]
        self.usercontrol.roomid = self.room
        self.pos = 'guest'
        response = requests.post(SERVERADDR+f'/check_in?room_id={room[:3]}',json={"guest_name":self.username})
        self.userselect.close()
        self.usercontrol.setWindowTitle(self.username)
        self.usercontrol.show()

    # 跳转到 login 窗口
    def show_login(self):
        self.main.close()
        # 格式化登录界面
        self.login = LoginUi()
        self.login.pushButton_login.clicked.connect(self.log_in)
        self.login.pushButton_return.clicked.connect(self.show_main)
        self.login.setWindowTitle(self.username)
        self.login.show()


    def show_manager_air(self):
        self.timer.start(FREQ)
        self.login.close()
        self.manager_air.stackedWidget.setCurrentIndex(0)
        self.manager_air.pushButton_onoff.clicked.connect(self.central_control)
        self.pos = 'air_admin'
        self.manager_air.setWindowTitle(self.username)
        self.manager_air.show()

    def show_manager_bill(self):
        self.timer.start(FREQ)
        self.login.close()
        self.manager_bill.stackedWidget.setCurrentIndex(0)
        self.manager_bill.listWidget_room.clear()
        rows = self.manager_bill.tableWidget_status.rowCount()
        for row in range(rows):
            item = self.manager_bill.tableWidget_status.item(row, 0)  # 获取第一列的单元格
            if item is not None:
                item.setText("")  # 清空文本
        self.manager_bill.comboBox_floor.setCurrentIndex(0)
        self.pos = 'reception'
        self.manager_bill.setWindowTitle(self.username)
        self.manager_bill.show()

    def log_in(self):
        if self.login.lineEdit_username.text() == "1" and self.login.lineEdit_password.text() == "123":
            self.show_manager_air()

        elif self.login.lineEdit_username.text() == "2" and self.login.lineEdit_password.text() == "123":
            self.show_manager_bill()

        else:
            self.login.label_error.setStyleSheet("color: red")

            self.login.label_error.setText("Incorrect username or password...Please try again")
            self.login.lineEdit_username.clear()
            self.login.lineEdit_password.clear()

    def select(self, index):
        self.userselect.comboBox_room.clear()
        # 获取对应的房间号选项

        self.userselect.comboBox_room.addItem('Click to select room number')
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
        arg = {
            "current_room_temp":past_state.env_temperature,
            "target_temp":past_state.target_temperature,
            "speed":past_state.speed
        }

        if (not past_state.working) and option != 0:
            return
        if option == 0:
            past_state.working = (past_state.working+1)%2
            if past_state.working:
                response = requests.post(SERVERADDR +f'/remote_control?device_id={device_id}',json={"command":'turn_on',"args":arg})
            else:
                response = requests.post(SERVERADDR +f'/remote_control?device_id={device_id}',json={"command":'turn_off',"args":arg})
        elif option ==1:
            if past_state.speed == 'low':
                past_state.speed = 'mid'
            elif past_state.speed == 'mid':
                past_state.speed = 'high'    
            elif past_state.speed == 'high':
                past_state.speed = 'low'
            arg['speed'] = past_state.speed
            response = requests.post(SERVERADDR +f'/remote_control?device_id={device_id}',json={"command":'set_speed',"args":arg})
        elif option == 2:
            past_state.target_temperature +=1
            arg['target_temp'] = past_state.target_temperature
            response = requests.post(SERVERADDR +f'/remote_control?device_id={device_id}',json={"command":'set_temperature',"args":arg})
        elif option == 3:
            past_state.target_temperature -=1
            arg['target_temp'] = past_state.target_temperature
            response = requests.post(SERVERADDR +f'/remote_control?device_id={device_id}',json={"command":'set_temperature',"args":arg})

        panel.isopen = past_state.working
        panel.current_speed = past_state.speed
        panel.current_mode = past_state.mode
        panel.cost = past_state.total_cost
        panel.target_temp = past_state.target_temperature
        panel.current_temp = past_state.env_temperature
        self.usercontrol.update_screen.emit()
        
    def central_control(self):
        #TODO：非法输入检测
        window = self.manager_air
        
        limit = [int(window.lineEdit_min.text()),int(window.lineEdit_max.text())]
        fee_rate = float(window.lineEdit_fee.text())
        arg = {
            "mode":"warm",
            "fee_rate":fee_rate,
            "valid_range_low":limit[0],
            "valid_range_high":limit[1]
        }
        requests.post(SERVERADDR+'/admin_control',json={"command":'set_valid_range',"args":arg})
        requests.post(SERVERADDR+'/admin_control',json={"command":'set_mode',"args":arg})
        requests.post(SERVERADDR+'/admin_control',json={"command":'turn_on',"args":arg})
        requests.post(SERVERADDR+'/admin_control',json={"command":'turn_off',"args":arg})
        requests.post(SERVERADDR+'/admin_control',json={"command":'set_price',"args":arg})

    def update_panel(self):
        panel = self.usercontrol
        time = datetime.now()
        response = requests.get(SERVERADDR +f'/get_device_status?device_id={panel.roomid}')
        response = json.loads(response.text)
        past_state = DeviceStatus(**response)
        panel.cost = past_state.total_cost
        panel.isopen = past_state.working
        panel.current_speed = past_state.speed
        panel.target_temp = past_state.target_temperature
        panel.current_temp = past_state.env_temperature
        self.usercontrol.update_screen.emit()

    def get_log(self):
        # 前台打印详单，调用/log/{room_id}接口
        #response = requests.get(SERVERADDR +f'/bill_detail?guest_name={self.username}')
        #roomid = 
        #response = requests.get(SERVERADDR+'/log/{room_id}')
        #print(response.text)
        #res = json.loads(response.text)
        response = requests.get(SERVERADDR+f'/bill_detail?guest_name={self.manager_bill.listWidget_room.currentItem().text()}')
        #print(response.text)
        res = json.loads(response.text)
        if type(res)!=list:
            return
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建 log.xlsx 文件的相对路径
        log_file_path_detail = os.path.join(current_dir, f'bill_detail/{self.manager_bill.listWidget_room.currentItem().text()}.xlsx')
        #print("log_file_path:\n",log_file_path)

        # 加载工作簿
        workbook_detail = openpyxl.Workbook()
        # 获取默认的工作表
        sheet = workbook_detail.active
        sheet.apeend('room_id','request_time','start_time','end_time','served_time','speed','cost','fee_rate','from_tem','to_tem')
        # 遍历二维列表，并将数据写入到工作表的单元格中
        for row in res:
            sheet.append(row)

        # 保存工作簿
        workbook_detail.save(log_file_path_detail)

    def get_bill(self):
        # 前台打印账单，调用@app.get('/cost/{room_id}')接口（接口需要自己实现）
        response = requests.get(SERVERADDR+f'/bill_cost?guest_name={self.manager_bill.listWidget_room.currentItem().text()}')
        print(response.text)
        res = json.loads(response.text)
        if len(res)!=4:
            return
        res_list = [key for key in res.keys()] + [value for value in res.values()]
    
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建 log.xlsx 文件的相对路径
        log_file_path_bill = os.path.join(current_dir, f'bill/{self.manager_bill.listWidget_room.currentItem().text()}.xlsx')
        #print("log_file_path:\n",log_file_path)

        # 加载工作簿
        workbook_bill = openpyxl.Workbook()
        # 获取默认的工作表
        sheet_bill = workbook_bill.active
        
        # 遍历二维列表，并将数据写入到工作表的单元格中
        sheet_bill.append(['total_cost','check_in_time','check_out_time','room_id'])
        sheet_bill.append(res_list[-4:])

        # 保存工作簿
        workbook_bill.save(log_file_path_bill)

    def check_out(self):
        # 前台退房，调用服务器@app.post('/{room_id}/check_out')接口
        #response = requests.post(SERVERADDR+f'/{room_id}/check_out')
        response = requests.post(SERVERADDR+f'/check_in?room_id={self.usercontrol.roomid[:3]}',json={"guest_name":self.username})
        
        print(response.text)
        print(self.usercontrol.roomid, '退房成功')

    def get_room_status(self, item):
        # 前台查看房间状态，例如
        #response = requests.get(SERVERADDR+'/state/rooms/101')
        #res = json.loads(response.text)获取该房间状态
        #然后将其显示到前端
        if item == None:
            return
        room_id = item.text()[:3]
        res = requests.get(SERVERADDR +f'/get_device_status?device_id={room_id}')
        res = json.loads(res.text)
        state = DeviceStatus(**res)
        """
        print(str(res.get('check_in_time', '')))
        check_in_time1 = str(res.get('check_in_time'))
        check_in_time2 = check_in_time1.split(".")[0]
        check_in_time3 = check_in_time2.replace("T", " ")
        temperature = QTableWidgetItem(str(res.get('temperature', '')))
        totalcost = QTableWidgetItem(str(res.get('totalcost', '')))
        if check_in_time3 == '0':
            check_in_time = QTableWidgetItem('未入住')
        else:
            check_in_time = QTableWidgetItem(check_in_time3)
        self.manager_bill.tableWidget_status.setItem(0, 0, check_in_time)
        """
        #print(str(res.get('check_in_time', '')))

        if res['working'] == 0:
            is_on = QTableWidgetItem('OFF')
        else:
            is_on = QTableWidgetItem('ON')
        self.manager_bill.tableWidget_status.setItem(0, 0, is_on)
        self.manager_bill.tableWidget_status.setItem(1, 0, QTableWidgetItem(str(state.mode)))
        self.manager_bill.tableWidget_status.setItem(2, 0, QTableWidgetItem(str(state.env_temperature)))
        self.manager_bill.tableWidget_status.setItem(3, 0, QTableWidgetItem(str(state.target_temperature)))
        self.manager_bill.tableWidget_status.setItem(4, 0, QTableWidgetItem(str(state.speed)))
        self.manager_bill.tableWidget_status.setItem(5, 0, QTableWidgetItem(str(round(state.total_cost,2))))

    def monitor(self):
        # 空调管理员监控各空调状态，前端界面需要一目了然
        # 用@app.get('/state/rooms')接口获取空调状态
        #self.timer.start(FREQ)
        response = requests.get(SERVERADDR+'/get_all_device_status')
        res=response.text
        res=json.loads(res)
        self.manager_air.addItem(res)
        self.manager_air.showscheduler()

    def timer_event(self):
        if self.pos == 'guest':
            self.update_panel()
        elif self.pos == 'air_admin':
            self.monitor()
        elif self.pos == 'reception':
            self.get_room_status(self.manager_bill.listWidget_room.currentItem())

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
        controller = Controller('101(109c)')
        controller.show_main()
        controller1 = Controller('102(109c2)')
        controller1.show_main()
        controller2 = Controller('103(113f)')
        controller2.show_main()
        controller3 = Controller('104(112b)')
        controller3.show_main()
        controller4 = Controller('105(112g)')
        controller4.show_main()
        controller5 = Controller('空调管理员')
        controller5.show_main()
        sys.exit(app.exec_())

    except Exception as e:
        print('未连接到服务器')
        print(e)
    
    
