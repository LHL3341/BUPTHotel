import pymysql
from typing import Optional
from datetime import datetime
import json
USER = "root"
PASSWORD = "root"
localhost = "127.0.0.1"
SCHEMAS = "bupthotel"

def Connection():#连接数据库
    try:
        db = pymysql.connect(host="localhost", user=USER,password=PASSWORD, database= SCHEMAS)
        print('数据库连接成功!')
        return True
    except pymysql.Error as e:
        print('数据库连接失败'+str(e))
        return False
    finally:
        db.close()
        

class UserInfo:
    """user_info"""
    user_name: str
    position: str
    password: str
    
    def __init__(self, user_name: str, position: str,password: str) -> None:
        self.password = password
        self.user_name = user_name
        self.position = position

    def Find_user_info(self,user_name_input):
        db = pymysql.connect(host="localhost", user=USER, password=PASSWORD, database=SCHEMAS)
        cur = db.cursor()
        sqlQuery = "SELECT * FROM user_info"
        ErrorCount = 0
        try:
            cur.execute(sqlQuery)
            results = cur.fetchall()
            for i in range(len(results)):
                if results[i][0] == user_name_input:
                    self.user_name = results[i][0]
                    self.position = results[i][1]
                    self.password =  results[i][2]
                    ErrorCount = ErrorCount + 1
            if ErrorCount == 0:
                print("此房间号不存在！")
                return False
            else:
                return True
        except pymysql.Error as e:
            print("数据获取失败：" + str(e))
        finally:
            db.close()

    def Insert_user_info(self,input_user_name,input_position,input_password):
        db = pymysql.connect(host="localhost", user=USER,password=PASSWORD,database=SCHEMAS)
        cur = db.cursor()
        sqlQuery = " INSERT INTO user_info (user_name,position,password) VALUE (%s,%s,%s) "#表格选取
        value = (input_user_name,input_position,input_password)
        try:
            cur.execute(sqlQuery, value)
            db.commit()
            return 1
        except pymysql.Error as error:
            print("数据加载失败：" + str(error))
            db.rollback()
            return 0
        finally:
            db.close()



    


class DeviceStatus:
    """device_status"""
    working: bool
    mode: str
    env_temperature: float
    target_temperature: float
    speed: str
    total_cost: float

    def __init__(self, working: bool, mode: str, env_temperature: float,target_temperature: float,speed: str,total_cost: float) -> None:
        self.working = working
        self.mode = mode
        self.env_temperature = env_temperature
        self.target_temperature = target_temperature
        self.speed = speed
        self.total_cost = total_cost


class RoomStatus:
    """room_status"""
    check_in_time: str
    check_out_time:str
    is_on: bool
    last_update: str
    mode: str
    room: str
    temperature: int
    totalcost: float
    wind_speed: int

    def __init__(self, check_in_time: str,check_out_time:str, is_on: bool, last_update: str, mode: str, room: str, temperature: int, totalcost: float, wind_speed: int) -> None:
        self.check_in_time = check_in_time
        self.check_out_time = check_out_time
        self.is_on = is_on
        self.last_update = last_update
        self.mode = mode
        self.room = room
        self.temperature = temperature
        self.totalcost = totalcost
        self.wind_speed = wind_speed

class DeviceConfig:
    """device_config"""
    device_no: str
    cost: float
    speed: float

    def __init__(self,device_no: str, cost: float, speed: float) -> None:
        self.device_no = device_no
        self.cost = cost
        self.speed = speed

    def Find_device_config(self,device_no_input):#对device_config表查询
        db = pymysql.connect(host="localhost", user=USER, password=PASSWORD, database=SCHEMAS)
        cur = db.cursor()
        ErrorCount = 0
        sqlQuery = "SELECT * FROM device_config"
        try:
            cur.execute(sqlQuery)
            results = cur.fetchall()
            for i in range(len(results)):
                if results[i][0] == device_no_input:
                    self.device_no = results[i][0]
                    self.speed = results[i][1]
                    self.cost =  results[i][2]
                    ErrorCount = ErrorCount + 1
            if ErrorCount == 0:
                print("此空调号不存在！")
                return False
            else:
                return True
        except pymysql.Error as e:
            print("数据获取失败：" + str(e))
        finally:
            db.close()

    def Insert_device_config(self,input_device_no,input_cost,input_speed):
        db = pymysql.connect(host="localhost", user=USER,password=PASSWORD,database=SCHEMAS)
        cur = db.cursor()
        sqlQuery = " INSERT INTO device_config (device_no,cost,speed) VALUE (%s,%s,%s) "#表格选取
        value = (input_device_no,input_cost,input_speed)
        try:
            cur.execute(sqlQuery, value)
            db.commit()
            return 1
        except pymysql.Error as error:
            print("数据加载失败：" + str(error))
            db.rollback()
            return 0
        finally:
            db.close()






class ReportEntry:
    """report_entry"""
    user_id: int
    check_in_time: Optional[str]
    check_out_time: Optional[str]
    cost: float
    #房间使用状态：1代表在使用、0代表未使用
    room: int
    power_consumption: float

    def __init__(self,user_id: str,check_in_time: str, check_out_time: str, cost: str, room: str,power_consumption:float ) -> None:
        self.user_id = user_id
        self.check_in_time = check_in_time
        self.check_out_time = check_out_time
        self.cost = cost
        self.room = room
        self.power_consumption = power_consumption


    def Find_report_entry(self,user_id_input):#对report_entry表查询
        db = pymysql.connect(host="localhost", user=USER, password=PASSWORD, database=SCHEMAS)
        cur = db.cursor()
        sqlQuery = "SELECT * FROM report_entry"
        NoneCount = 0
        try:
            cur.execute(sqlQuery)
            results = cur.fetchall()
            for i in range(len(results)):
                if results[i][0] == user_id_input:
                    self.user_id = results[i][0]
                    self.check_in_time = results[i][1]
                    self.check_out_time =  results[i][2]
                    self.cost = results[i][3]
                    self.room = results[i][4]
                    self.power_consumption = results[i][5]
                    NoneCount = NoneCount + 1
            if NoneCount == 0:
                print("此user_id不存在")
                return False
            else:
                return True
        except pymysql.Error as e:
            print("数据获取失败：" + str(e))
        finally:
            db.close()

    def Insert_report_entry(self,input_user_id,input_check_in_time,input_check_out_time,input_cost,input_room,input_power_consumption):
        db = pymysql.connect(host="localhost", user=USER,password=PASSWORD,database=SCHEMAS)
        cur = db.cursor()
        sqlQuery = " INSERT INTO report_entry (userID,check_in_time,check_out_time,cost,room,power_consumption) VALUE (%s,%s,%s,%s,%s,%s) "#表格选取
        value = (input_user_id,input_check_in_time,input_check_out_time,input_cost,input_room,input_power_consumption)
        try:
            cur.execute(sqlQuery, value)
            db.commit()
            return 1
        except pymysql.Error as error:
            print("数据加载失败：" + str(error))
            db.rollback()
            return 0
        finally:
            db.close()

#Connection()
#rel = ReportEntry(0,0,0,0,0,0)
#rel.Insert_report_entry(213341,"2023-01-02 21:22:11",'2023-12-11 14:00:00',4,5,6)

    
class LogEntry:
    """log_entry
    房间号、请求时间、服务开始时间、服务结束时间、服务时长、开关、当前室温、目标温度、模式、风速、当前费用、费率、用户名
    """
    room: str
    request_time: datetime
    start_time: datetime
    end_time: datetime
    duration: datetime
    speed: int
    period_cost: float
    fee_rate:float
    from_tem: float
    to_tem: float
    

    def __init__(self,
                room: str,
                request_time: datetime,
                start_time: datetime,
                end_time: datetime,
                duration: datetime,
                speed: int,
                period_cost: float,
                fee_rate: float,
                from_tem: float,
                to_tem: float
                ) -> None:
        self.room= room
        self.request_time=request_time
        self.start_time=start_time
        self.end_time=end_time
        self.duration=duration
        self.speed=speed
        self.period_cost=period_cost
        self.fee_rate = fee_rate
        self.from_tem=from_tem
        self.to_tem=to_tem

    def Find_log_entry(self,room_input):#对log_entry表查询
        db = pymysql.connect(host="localhost", user=USER, password=PASSWORD, database=SCHEMAS)
        cur = db.cursor()
        sqlQuery = "SELECT * FROM log_entry"
        ErrorCount = 0
        try:
            cur.execute(sqlQuery)
            results = cur.fetchall()
            for i in range(len(results)):
                if results[i][0] == room_input :
                    self.room= results[i][0]
                    self.request_time=results[i][1]
                    self.start_time=results[i][2]
                    self.end_time=results[i][3]
                    self.duration=results[i][4]
                    self.speed=results[i][5]
                    self.period_cost=results[i][6]
                    self.fee_rate=results[i][7]
                    self.from_tem=results[i][8]
                    self.to_tem=results[i][9]
                    ErrorCount = ErrorCount + 1
            if ErrorCount == 0:
                print("此房间号不存在！")
                return False
            else:
                return True
        except pymysql.Error as e:
            print("数据获取失败：" + str(e))
        finally:
            db.close()



    def Insert_log_entry(self):
        db = pymysql.connect(host="localhost", user=USER,password=PASSWORD,database=SCHEMAS)
        cur = db.cursor()
        sqlQuery = " INSERT INTO log_entry (room,request_time,start_time,end_time,duration,speed,period_cost,fee_rate,from_tem,to_tem)\
              VALUE (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "#表格选取
        value = (
                self.room,
                self.request_time,
                self.start_time,
                self.end_time,
                self.duration,
                self.speed,
                self.period_cost,
                self.fee_rate,
                self.from_tem,
                self.to_tem)
        try:
            cur.execute(sqlQuery, value)
            db.commit()
            return 1
        except pymysql.Error as error:
            print("数据加载失败：" + str(error))
            db.rollback()
            return 0
        finally:
            db.close()

def Export_room_log(room,check_in,check_out):
    
    db = pymysql.connect(host="localhost", user=USER,password=PASSWORD,database=SCHEMAS)
    cur = db.cursor()
    sqlQuery = f"SELECT * FROM log_entry WHERE room = '{room}' AND request_time BETWEEN '{check_in}' AND '{check_out}'"#表格选取
    try:
        cur.execute(sqlQuery)
        results = cur.fetchall()
        print(results)
        return results
    except pymysql.Error as error:
        print("数据加载失败：" + str(error))
        db.rollback()
        return 0
    finally:
        db.close()



#Connection()
#rel = LogEntry(None,None,None,None,None,0,0,0,None,0,0,0,None)
#num = rel.Find_log_entry("2-33")
#print("num:\n",num)
#rel = LogEntry("2-111",31,1,2,1,'2023-12-11 14:00:00',456)
#rel.Insert_log_entry()
#res = Export_room_log('202','"2023-11-27 16:44:55"','"2023-11-27 16:46:40"')
#print(res)




#Connection()
#rel = LogEntry("2-111",31,1,2,1,'2023-12-11 14:00:00',456)
#rel.Insert_log_entry()
#res = Export_room_log('202','"2023-11-27 16:44:55"','"2023-11-27 16:46:40"')
#print(res)