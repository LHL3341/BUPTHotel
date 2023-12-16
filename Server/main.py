# Server
# written by LHL
import os
import sys
sys.path.append(os.path.abspath('..'))
sys.path.append(os.path.abspath('.'))
from fastapi import FastAPI, Body
from entity import *
from copy import deepcopy
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler

# Constants for default settings and configurations

DEFAULT_TARGET_TEMP = 22
TIMESLICE = 10   # 10秒当作1分钟，可调，如TIMESLICE=30,则30秒作一分钟
FREQ = 1
DEFAULT_CHECKOUT = datetime(2035,1,1)
SPEED = {'low':0,'mid':1,'high':2}
WINDSPEED = {'low':0.33,'mid':0.5,'high':1}
MODE = {'warm':1,'cold':0}

# Class representing a hotel room
class Room:
    #房间
    def __init__(self,id):
        # Initialize room with default values and device status
        self.roomid = id
        self.isused = False
        self.default_tmp = 24
        self.checkin = datetime.now()
        self.checkout = DEFAULT_CHECKOUT
        self.username = ''
        self.device = DeviceStatus(False,'warm',24,DEFAULT_TARGET_TEMP,'mid',0)

    def get_status(self):
        # Get the current status of the room's device
        return self.device
        #return RoomStatus(self.checkin,self.checkout,self.device.is_on,self.device.last_update,self.device.mode
        #                  ,self.device.room,self.device.temperature,self.totalcost,self.device.wind_speed)
    def update_status(self,roomstatus):
        # Update room status with given room status information
        self.checkin = roomstatus.check_in_time
        self.checkout = roomstatus.check_out_time
        self.device.is_on = roomstatus.is_on
        self.device.last_update = roomstatus.last_update
        self.device.mode = roomstatus.mode
        self.device.room = roomstatus.room
        self.device.temperature = roomstatus.temperature
        self.device.wind_speed = roomstatus.wind_speed
    
    def update_device(self,devicetatus):
         # Update the device status of the room
        self.device.working = devicetatus.working
        self.device.mode = devicetatus.mode
        self.device.env_temperature = devicetatus.env_temperature
        self.device.target_temperature = devicetatus.target_temperature
        self.device.speed = devicetatus.speed
        self.device.total_cost = devicetatus.total_cost

    def Export_room_log(self,check_in,check_out):
        # Export room log for a specified time period
    
        db = pymysql.connect(host="localhost", user=USER,password=PASSWORD,database=SCHEMAS)
        cur = db.cursor()
        sqlQuery = f"SELECT * FROM log_entry WHERE room = '{self.roomid}' AND request_time BETWEEN '{check_in}' AND '{check_out}'"#表格选取
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

    def turnon(self):
        # Turn on the device in the room
        self.device.working=True

    def turnoff(self):
        # Turn off the device in the room
        self.device.working=False

    def setspeed(self,speed):
         # Set the speed of the device in the room
        self.device.speed =speed
    
    def settemp(self,temp):
        # Set the temperature of the device in the room
        self.device.target_temperature = temp

# Class representing a task in the scheduler
class Task:
    roomid:str
    speed:int
    request_time:datetime
    start_time:datetime
    end_time:datetime
    served_time:float
    start_tmp:float
    end_tmp:float
    cost:float
    
    def __init__(self, roomid,speed,start_tmp):
        # Initialize task with room ID, speed, and starting temperature
        self.request_time = datetime.now()
        self.roomid = roomid
        self.speed =speed
        self.start_time = None
        self.end_time = None
        self.start_tmp = start_tmp
        self.end_tmp = None
        self.served_time = 0
        self.cost =0

# Scheduler class for managing tasks
class Scheduler:
    #调度器
    def __init__(self):
        # Initialize scheduler with waiting and serving lists
        self.wait_list = {0:[],1:[],2:[]}
        self.serving_list = {0:None,1:None,2:None}#只有三个实例资源
    
    def isEmpty(self):
        # Check if the scheduler has an empty slot
        for k,v in self.serving_list.items():
            if v == None:
                return k
        return -1
    
    def isPreemptable(self,item):
        # Check if a task can be preempted
        max = 0
        maxid = -1
        for i in range(3):
            j = item.speed - self.serving_list[i].speed
            if j > max:
                max = j
                maxid = i
        return maxid
        
    def addItem(self,roomid,speed,env_tmp):
        # Add a new task to the scheduler
        # 收到新的请求
        item = Task(roomid,speed,env_tmp)
        time = datetime.now()
        i = self.isEmpty()
        if i >=0:
            #若空，则直接开始服务
            print((roomid,speed),'直接使用实例',i)
            self.serving_list[i] = item
            item.start_time = time
        elif self.isPreemptable(item)!=-1:
            #若优先级更高，则抢占
            j = self.isPreemptable(item)
            preempted_item = self.serving_list[j]
            print((roomid,speed),"从",(preempted_item.roomid,preempted_item.speed),'抢占实例',j)
            self.wait_list[preempted_item.speed].append(self.serving_list[j])
            item.start_time = time
            self.serving_list[j] = item
        else:
            self.wait_list[speed].append(item)
        
    def RemoveItem(self,roomid):
        # Remove a task from the scheduler
        for k,v in self.serving_list.items():
            if v != None and roomid == v.roomid:
                self.serving_list[k] = None
                room = hotel.rooms[roomid]
                device = room.device
                v.end_time = datetime.now()
                v.end_tmp = device.env_temperature

                LogEntry(v.roomid,
                        v.request_time,
                        v.start_time,
                        v.end_time,
                        v.served_time,
                        v.speed,
                        v.cost,
                        hotel.central.cost,
                        v.start_tmp,
                        v.end_tmp
                        ).Insert_log_entry()
        for i, j in self.wait_list.items():
            if j != []:
                for k in j:
                    if roomid == k.roomid:
                        j.remove(k)

    def Insert(self, priority=[2,1,0]):
        # Insert tasks into empty slots based on priority
        i = self.isEmpty()
        if i == -1:
            return
        for j in priority:
            waitlist = self.wait_list[j]
            if waitlist!=[] and self.serving_list[i]==None:
                self.serving_list[i] = waitlist[0]
                print((waitlist[0].roomid,waitlist[0].speed),f'使用空闲实例{i}')
                if waitlist[0].start_time== None:
                    waitlist[0].start_time = datetime.now()
                waitlist.remove(waitlist[0])
                break

    def Request(self,roomid,speed,env_tmp):
        # Handle a new request
        item = Task(roomid,speed,env_tmp)
        self.wait_list[speed].append(item)        

    def clear(self):
        # Clear all tasks from the scheduler
        for k, v in self.wait_list.items():
            for i in v:
                self.RemoveItem(i.roomid)
        for k, v in self.serving_list.items():
            if v!=None:
                self.RemoveItem(v.roomid)
        self.wait_list = {0:[],1:[],2:[]}
        self.serving_list = {0:None,1:None,2:None}

# Class representing the central air conditioning system
class CentralAir:
    #空调配置
    def __init__(self):
        # Initialize the central air system with default settings
        self.scheduler = Scheduler()
        self.isopen = True  #总开关
        self.cost = 1 #费率
        self.limit = [16,24]  #温度范围
        self.mode = 'warm'
    def turnon(self):
        # Turn on the central air system
        self.isopen=True
        
    # Turn off the central air system
    def turnoff(self):
        self.isopen=False
        self.scheduler.clear()

    def setfeerate(self,x):
        # Set the fee rate for the central air system
        self.cost = x
    def setvalid(self,range):
        # Set the valid temperature range for the central air system
        self.limit = range

    def setmode(self,mode):
        # Set the mode of the central air system
        self.mode = mode

# Class representing a hotel
class Hotel:
    #酒店
    def __init__(self):
         # Initialize the hotel with rooms and central air system
        self.test= 1
        self.central = CentralAir()   
        self.slice_num =0 
        self.rooms = {}
        for layer in [1,2,3,4]:
            for i in range(1,11):
                if i ==10:
                    roomid = f'{layer}10'
                else:
                    roomid = f'{layer}0{i}'
                self.rooms.update({roomid:Room(roomid)})

    def getroomstate(self,roomid):
        # Get the state of a specific room
        return self.rooms[roomid].get_status()
    
    def updateroom(self,roomstatus):
        # Update room status based on roomstatus information
        roomid = roomstatus.room
        oldstatus = self.rooms[roomid].get_status()
        if not oldstatus.is_on and roomstatus.is_on:
            self.scheduler.addItem(roomid,roomstatus.last_update,roomstatus.wind_speed)
        elif oldstatus.is_on and not roomstatus.is_on:
            self.scheduler.RemoveItem(roomid,roomstatus.last_update,roomstatus.wind_speed)
        elif oldstatus.wind_speed != roomstatus.wind_speed:
            self.scheduler.RemoveItem(roomid,roomstatus.last_update,roomstatus.wind_speed)
            self.scheduler.Wait(roomid,roomstatus.last_update,roomstatus.wind_speed)
            self.scheduler.Insert()
        self.rooms[roomid].update_status(roomstatus)
        self.schedule()
        
        
    def updatedevice(self,devicestatus):
        # Update device status based on devicestatus information
        roomid = devicestatus.room
        oldstatus = self.rooms[roomid].get_status()
        if not oldstatus.is_on and devicestatus.is_on:
            self.scheduler.addItem(roomid,devicestatus.last_update,devicestatus.wind_speed)
        elif oldstatus.is_on and not devicestatus.is_on:
            self.scheduler.RemoveItem(roomid,devicestatus.last_update,devicestatus.wind_speed)
        elif oldstatus.wind_speed != devicestatus.wind_speed:
            self.scheduler.RemoveItem(roomid,devicestatus.last_update,devicestatus.wind_speed)
            self.scheduler.Wait(roomid,devicestatus.last_update,devicestatus.wind_speed)
            self.scheduler.Insert()
        self.rooms[roomid].update_device(devicestatus)
        #LogEntry(devicestatus.room,devicestatus.temperature,devicestatus.wind_speed,0,devicestatus.is_on,datetime.now(),self.rooms[devicestatus.room].checkin).Insert_log_entry()
        self.schedule()
    
    def Robin(self):
        # Round-robin scheduling method

        for k,v in self.central.scheduler.serving_list.items():
            if v!=None and v.served_time%(TIMESLICE*2)==0 and v.served_time!=0:
                if self.central.scheduler.wait_list[v.speed]!=[]:
                    self.central.scheduler.wait_list[v.speed].append(v)
                    self.central.scheduler.serving_list[k] = None
        self.central.scheduler.Insert()
    
    def update_temp(self):
        # Update the temperature in all rooms
        interval = FREQ/TIMESLICE
        served = [self.central.scheduler.serving_list[i].roomid for i in range(3) if self.central.scheduler.serving_list[i]!=None]
        for k, v in self.rooms.items():
            if k not in served:
                if abs(v.device.env_temperature - v.default_tmp) <=0.5*interval:
                    v.device.env_temperature = v.default_tmp
                elif v.device.env_temperature > v.default_tmp:
                    v.device.env_temperature -=0.5*interval
                else:
                    v.device.env_temperature +=0.5*interval
            
        for k, v in self.central.scheduler.serving_list.items():
            if v!=None:
                device = self.rooms[v.roomid].device
                slide = WINDSPEED[device.speed]*interval
                if abs(device.target_temperature - device.env_temperature)<=slide:
                    device.env_temperature = device.target_temperature
                    # 释放资源
                    print(v.roomid,'到达目标温度，释放资源')
                    device.working = False
                    self.central.scheduler.RemoveItem(v.roomid)
                    self.central.scheduler.Insert()
                    
                elif device.env_temperature < device.target_temperature:
                    device.env_temperature += slide
                else:
                    device.env_temperature -= slide
        if self.slice_num % TIMESLICE == 0 and self.slice_num!=0:
            print("时间片",int(self.slice_num//TIMESLICE))
            print("服务队列：",[(self.central.scheduler.serving_list[i].roomid,self.central.scheduler.serving_list[i].speed)  for i in range(3) if self.central.scheduler.serving_list[i]!=None])
            print("等待队列：",[[room.roomid for room in self.central.scheduler.wait_list[i]]  for i in range(3) if self.central.scheduler.wait_list[i]!=None])
        self.slice_num +=1
            
    def schedule(self):
        # Schedule tasks for room devices
        room_ls = [self.scheduler.serving_list[i].roomid  for i in range(3) if self.scheduler.serving_list[i]!=None]
        for k, v in hotel.rooms.items():
            if v.device.room in room_ls and not v.device.is_on:
                v.device.is_on = True
                v.device.last_update = datetime.now()

            elif v.device.is_on and v.device.room not in room_ls:
                v.device.is_on = False
                # TODO:产生一条详单记录 Logentry
                v.device.last_update = datetime.now()

    def checkout(self,room_id,guest_name):
        # Check out a guest from a room
        if not self.rooms[room_id].isused:
            room = self.rooms[room_id]
            room.isused = False
            room.checkout = DEFAULT_CHECKOUT
            room.username = ''
            room.device = DeviceStatus(False,False,24,DEFAULT_TARGET_TEMP,'mid',0)
    
    def checkin(self,room_id,guest_name):
        # Check in a guest into a room
        if not self.rooms[room_id].isused:
            room = self.rooms[room_id]
            room.isused = True
            room.checkin = datetime.now()
            room.username = str(guest_name)
            print(room.username+'入住')

    def remote_control(self,device_id, body):
        # Remote control function for devices in rooms
        if self.test:
            self.test =0
            timer.start()
        # turn_on, turn_off, set_temperature, set_speed
        command, args = body["command"], body["args"]
        room = self.rooms[device_id]
        if command == "turn_on":
            room.turnon()
            self.central.scheduler.addItem(device_id,SPEED[room.device.speed],room.device.env_temperature)
            
        elif command == "turn_off":
            room.turnoff()
            self.central.scheduler.RemoveItem(device_id)
            self.central.scheduler.Insert()

        elif command == "set_temperature":
            room.settemp(args["target_temp"])

        elif command == "set_speed":
            self.central.scheduler.RemoveItem(device_id)
            if room.device.speed == 'high':
                self.central.scheduler.Insert()
            elif room.device.speed == 'low':
                self.central.scheduler.Insert([2,1])
            else:
                self.central.scheduler.Insert([2])
            room.setspeed(args["speed"])
            self.central.scheduler.addItem(device_id,SPEED[room.device.speed],room.device.env_temperature)

    def admin_control(self,command, args):
        # Administrative control for the central air system
        if command == "turn_on":
            self.central.turnon()
        elif command == "turn_off":
            self.central.turnoff()
            self.central.scheduler.clear()
            for k, v in self.rooms.items():
                v.device.working = False
        elif command == "set_mode":
            self.central.setmode(args["mode"]) 
        #TODO
        elif command == "set_valid_range":
            self.central.setvalid([args["valid_range_low"],args["valid_range_high"]])
            for k, v in self.rooms.items():
                past_temp = v.device.target_temperature
                v.device.target_temperature = max(args["valid_range_low"],past_temp)
                v.device.target_temperature = min(args["valid_range_high"],v.device.target_temperature)
        #TODO
        elif command == "set_price":
            self.central.setfeerate(args["fee_rate"]) 
        
# Function to simulate the hotel environment
def simulate():
    
    #del hotel.rooms['101']
    #del hotel.rooms['102']
    #del hotel.rooms['103']
    #del hotel.rooms['104']
    #del hotel.rooms['105']
    #hotel.rooms.update({'101(109c)':Room('101(109c)')})
    #hotel.rooms.update({'102(109c2)':Room('102(109c2)')})
    #hotel.rooms.update({'103(113f)':Room('103(113f)')})
    #hotel.rooms.update({'104(112b)':Room('104(112b)')})
    #hotel.rooms.update({'105(112g)':Room('105(112g)')})
    #hotel.rooms['101(109c)'].default_tmp = 10
    #hotel.rooms['102(109c2)'].default_tmp = 15
    #hotel.rooms['103(113f)'].default_tmp = 18
    #hotel.rooms['104(112b)'].default_tmp = 12
    #hotel.rooms['105(112g)'].default_tmp = 14
    #hotel.rooms['101(109c)'].device.env_temperature = 10
    #hotel.rooms['102(109c2)'].device.env_temperature = 15
    #hotel.rooms['103(113f)'].device.env_temperature = 18
    #hotel.rooms['104(112b)'].device.env_temperature = 12
    #hotel.rooms['105(112g)'].device.env_temperature = 14
    hotel.rooms['101'].default_tmp = 10
    hotel.rooms['102'].default_tmp = 15
    hotel.rooms['103'].default_tmp = 18
    hotel.rooms['104'].default_tmp = 12
    hotel.rooms['105'].default_tmp = 14
    hotel.rooms['101'].device.env_temperature = 10
    hotel.rooms['102'].device.env_temperature = 15
    hotel.rooms['103'].device.env_temperature = 18
    hotel.rooms['104'].device.env_temperature = 12
    hotel.rooms['105'].device.env_temperature = 14

if Connection():
    app = FastAPI()
    hotel = Hotel()
    simulate()
    timer = AsyncIOScheduler()
    
    
@timer.scheduled_job('interval',seconds=FREQ)
async def timer_event():
    # 计费
    cost = hotel.central.cost
    for k, v in hotel.central.scheduler.serving_list.items():
        if v != None:
            device = hotel.rooms[v.roomid].device
            device.total_cost += cost*WINDSPEED[device.speed]*(FREQ/TIMESLICE)
            v.cost += cost*WINDSPEED[device.speed]*(FREQ/TIMESLICE)
            v.served_time += (FREQ/TIMESLICE)
        
    # 调度
    hotel.Robin()
    hotel.update_temp()


@app.get("/")
async def root():
    return {"message": "成功连接到服务器！"}

@app.get("/login")
async def login():
    return {"status":"login success"}

@app.get("/logout")
async def logout():
    return {"status":"logouted"}

@app.post('/remote_control')
async def remote_control(device_id, body=Body(None)):
    """if hotel.test:
        hotel.test =0
        timer.start()

    # turn_on, turn_off, set_temperature, set_speed
    command, args = body["command"], body["args"]
    room = hotel.rooms[device_id]
    if command == "turn_on":
        room.device.working = True
        hotel.central.scheduler.addItem(device_id,SPEED[room.device.speed],room.device.env_temperature)
        
    elif command == "turn_off":
        room.device.working = False
        hotel.central.scheduler.RemoveItem(device_id)
        hotel.central.scheduler.Insert()

    elif command == "set_temperature":
        room.device.target_temperature = args["target_temp"]

    elif command == "set_speed":
        hotel.central.scheduler.RemoveItem(device_id)
        if room.device.speed == 'high':
            hotel.central.scheduler.Insert()
        elif room.device.speed == 'low':
            hotel.central.scheduler.Insert([2,1])
        else:
            hotel.central.scheduler.Insert([2])
        room.device.speed = args["speed"]
        hotel.central.scheduler.addItem(device_id,SPEED[room.device.speed],room.device.env_temperature)"""
        
    hotel.remote_control(device_id,body)
    return {"status":"success!"}

@app.get('/get_panel_status')
async def update_panel(device_id):
    dic = hotel.getroomstate(device_id).__dict__
    del dic['mode']
    del dic['total_cost']
    return dic

@app.post('/admin_control')
async def admin_control(body=Body(None)):
    # turn_on, turn_off, set_mode, set_valid_range, set_price
    command, args = body["command"], body["args"]
    hotel.admin_control(command,args)
    return {"status":"success!"}

@app.get('/get_all_device_status')
async def get_all_device_status():
    res = []
    for key, value in hotel.rooms.items():
        dic = hotel.getroomstate(key).__dict__.copy()
        dic["room_id"] = key
        res.append(dic)
    return {"device_list":res}

@app.get('/get_device_status')
async def get_device_status(device_id):
    return hotel.getroomstate(device_id).__dict__

@app.post('/check_in')
async def check_in(room_id, body=Body(None)):
    if room_id == '':
        return {"detail":"房间为空"}
    guest_name = body["guest_name"]
    hotel.checkin(room_id,guest_name)

        #room.device = DeviceStatus(False,'warm',24,DEFAULT_TARGET_TEMP,'mid',0)
    
    return {"status":"success!"}

@app.post('/check_out')
async def check_out(room_id, body=Body(None)):
    guest_name = body["guest_name"]
    hotel.check_out(room_id,guest_name)

        #hotel.updateroom(newstate)
        # TODO:产生一条详单记录 Logentry
    return {"status":"success!"}

@app.get('/bill_cost')
async def get_bill(guest_name):
    """
    计算账单
    根据每个房间记录
    返回空调费和房费
    房费500每晚，空调费根据详单和费率计算
    """
    for k,v in hotel.rooms.items():
        if v.username == guest_name:
            room = v
            #res = Export_room_log(room.roomid,room.checkin,room.checkout)
            res = room.Export_room_log(room.checkin,room.checkout)
            ttcost = 0
            for entry in res:
                ttcost += entry[6]
            print(guest_name+'共花费'+str(ttcost))
            res = {
                'total_cost':ttcost,
                'check_in_time':room.checkin,
                'check_out_time':room.checkout,
                'room_id':room.roomid
            }
            return res
    print("用户不存在")
    return {"detail":"用户不存在"}
    


@app.get('/bill_detail')
async def get_log(guest_name):
    """
    返回某个房间的详单
    """
    for k,v in hotel.rooms.items():
        if v.username == guest_name:
            room = v
            #res = Export_room_log(room.roomid,room.checkin,room.checkout)
            res = room.Export_room_log(room.checkin,room.checkout)
            return res
    print("用户不存在")
    return {"detail":"用户不存在"}

@app.post('/get_daily_report')
async def get_daily_report(body=Body(None)):
    """
    计算报表
    """
    body = json.loads(body)
    date = body['date']
    pass

@app.post('/get_weekly_report')
async def get_weekly_report(body=Body(None)):
    """
    计算报表
    """
    body = json.loads(body)
    date = body['date']
    pass


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app,host='127.0.0.1',port=10086)
    