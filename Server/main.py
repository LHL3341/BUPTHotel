import os
import sys
sys.path.append(os.path.abspath('..'))
sys.path.append(os.path.abspath('.'))
from fastapi import FastAPI, Body
from entity import *
from copy import deepcopy
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler

DEFAULT_TARGET_TEMP = 25
TIMESLICE = 10
FREQ = 1
SPEED = {'low':0,'mid':1,'high':2}

class Room:
    #房间
    def __init__(self,id):
        self.roomid = id
        self.isused = False
        self.default_tmp = 25
        self.checkin = datetime.now()
        self.checkout = datetime.now()
        self.username = ''
        self.device = DeviceStatus(False,False,24,DEFAULT_TARGET_TEMP,'mid',0)

    def get_status(self):
        return self.device
        #return RoomStatus(self.checkin,self.checkout,self.device.is_on,self.device.last_update,self.device.mode
        #                  ,self.device.room,self.device.temperature,self.totalcost,self.device.wind_speed)
    def update_status(self,roomstatus):
        self.checkin = roomstatus.check_in_time
        self.checkout = roomstatus.check_out_time
        self.device.is_on = roomstatus.is_on
        self.device.last_update = roomstatus.last_update
        self.device.mode = roomstatus.mode
        self.device.room = roomstatus.room
        self.device.temperature = roomstatus.temperature
        self.device.wind_speed = roomstatus.wind_speed
    
    def update_device(self,devicetatus):
        self.device.working = devicetatus.working
        self.device.mode = devicetatus.mode
        self.device.env_temperature = devicetatus.env_temperature
        self.device.target_temperature = devicetatus.target_temperature
        self.device.speed = devicetatus.speed
        self.device.total_cost = devicetatus.total_cost

class Task:
    roomid:str
    speed:int
    request_time:datetime
    start_time:datetime
    end_time:datetime
    served_time:float
    
    def __init__(self, roomid,speed):
        self.request_time = datetime.now()
        self.roomid = roomid
        self.speed =speed
        self.start_time = None
        self.served_time = 0

class Scheduler:
    #调度器
    def __init__(self):
        self.wait_list = {0:[],1:[],2:[]}
        self.serving_list = {0:None,1:None,2:None}#只有三个实例资源
    
    def isEmpty(self):
        for k,v in self.serving_list.items():
            if v == None:
                return k
        return -1
    
    def isPreemptable(self,item):
        max = 0
        maxid = -1
        for i in range(3):
            j = item.speed - self.serving_list[i].speed
            if j > max:
                max = j
                maxid = i
        print(maxid)
        return maxid
        
    def addItem(self,roomid,speed):
        # 收到新的请求
        item = Task(roomid,speed)
        time = datetime.now()
        i = self.isEmpty()
        if i >=0:
            #若空，则直接开始服务
            self.serving_list[i] = item
            item.start_time = time
        elif self.isPreemptable(item)!=-1:
            #若优先级更高，则抢占
            j = self.isPreemptable(item)
            preempted_item = self.serving_list[j]
            print(roomid+"抢占"+preempted_item.roomid)
            self.wait_list[preempted_item.speed].append(self.serving_list[j])
            item.start_time = time
            self.serving_list[j] = item
        else:
            self.wait_list[speed].append(item)
        
    def RemoveItem(self,roomid):
        for k,v in self.serving_list.items():
            if v != None and roomid == v.roomid:
                self.serving_list[k] = None
                v.end_time = datetime.now()
                break
        room = hotel.rooms[roomid]
        device = room.device
        LogEntry(v.roomid,v.request_time,v.start_time,v.end_time,v.served_time,device.working,device.env_temperature,
                 device.target_temperature,device.mode,device.speed,device.totalcost,room.username).Insert_log_entry()
        self.Insert()

    def Insert(self, priority=[2,1,0]):
        i = self.isEmpty()
        for j in priority:
            waitlist = self.wait_list[j]
            if waitlist!=[]:
                self.serving_list[i] = waitlist[0]
                print('插入'+waitlist[0].roomid)
                if waitlist[0].start_time== None:
                    waitlist[0].start_time = datetime.now()
                waitlist.remove(waitlist[0])
                break

    def Request(self,roomid,speed):
        item = Task(roomid,speed)
        self.wait_list[speed].append(item)        

    def clear(self):
        for k, v in self.wait_list:
            for i in v:
                self.RemoveItem(i.roomid)
        for k, v in self.serving_list:
            self.RemoveItem(v.roomid)
        self.wait_list = {0:[],1:[],2:[]}
        self.serving_list = {0:None,1:None,2:None}



class CentralAir:
    #空调配置
    def __init__(self):
        self.scheduler = Scheduler()
        self.isopen = True  #总开关
        self.cost = [0.5,1,2] #低中高速风费率
        self.limit = [16,24]  #温度范围
        self.mode = True

class Hotel:
    #酒店
    def __init__(self):
        self.central = CentralAir()   
        self.rooms = {}
        for layer in [1,2,3,4]:
            for i in range(1,11):
                if i ==10:
                    roomid = f'{layer}10'
                else:
                    roomid = f'{layer}0{i}'
                self.rooms.update({roomid:Room(roomid)})
    def getroomstate(self,roomid):
        return self.rooms[roomid].get_status()
    
    def updateroom(self,roomstatus):
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
        LogEntry(devicestatus.room,devicestatus.temperature,devicestatus.wind_speed,0,devicestatus.is_on,datetime.now(),self.rooms[devicestatus.room].checkin).Insert_log_entry()
        self.schedule()
    
    def Robin(self):

        scheduler = self.central.scheduler
        for k,v in scheduler.serving_list.items():
            if v!=None and v.served_time%TIMESLICE==0 and v.served_time!=0:
                if scheduler.wait_list[v.speed]!=[]:
                    print(scheduler.wait_list)
                    scheduler.wait_list[v.speed].append(v)
                    scheduler.serving_list[k] = None
                    scheduler.Insert([v.speed])
        
    def schedule(self):
        room_ls = [self.scheduler.serving_list[i]['roomid']  for i in range(3) if self.scheduler.serving_list[i]!=None]
        for k, v in hotel.rooms.items():
            if v.device.room in room_ls and not v.device.is_on:
                v.device.is_on = True
                v.device.last_update = datetime.now()

            elif v.device.is_on and v.device.room not in room_ls:
                v.device.is_on = False
                # TODO:产生一条详单记录 Logentry
                v.device.last_update = datetime.now()



if Connection():
    app = FastAPI()
    hotel = Hotel()
    timer = AsyncIOScheduler()
    timer.start()
    
@timer.scheduled_job('interval',seconds=FREQ)
async def timer_event():
    # 计费
    servelist = hotel.central.scheduler.serving_list
    cost = hotel.central.cost
    for k, v in servelist.items():
        if v != None:
            device = hotel.rooms[v.roomid].device
            device.total_cost += cost[SPEED[device.speed]]*(FREQ/60)
            v.served_time += FREQ
        
    # 调度
    hotel.Robin()

@timer.scheduled_job('interval',seconds=10)
async def update_temp():

    servelist = hotel.central.scheduler.serving_list
    served = [servelist[i].roomid for i in range(3) if servelist[i]!=None]
    print(served)
    for k, v in hotel.rooms.items():
        if k not in served:
            if abs(v.device.env_temperature - v.default_tmp) <=0.5:
                v.device.env_temperature = v.default_tmp
            elif v.device.env_temperature > v.default_tmp:
                v.device.env_temperature -=0.5
            else:
                v.device.env_temperature +=0.5
        
    for k, v in servelist.items():
        if v!=None:
            device = hotel.rooms[v.roomid].device
            if abs(device.target_temperature - device.env_temperature)<=0.5:
                device.env_temperature = device.target_temperature
                # 释放资源

            elif device.env_temperature < device.target_temperature:
                device.env_temperature += 0.5
            else:
                device.env_temperature -= 0.5



@app.get("/")
async def root():
    return {"message": "成功连接到服务器！"}

@app.post("/login")
async def login():
    return {"status":"login success"}

@app.post("/logout")
async def logout():
    return {"status":"logouted"}

@app.post('/remote_control')
async def remote_control(device_id, body=Body(None)):
    # turn_on, turn_off, set_temperature, set_speed
    scheduler = hotel.central.scheduler
    command, args = body["command"], body["args"]
    room = hotel.rooms[device_id]
    if command == "turn_on":
        room.device.working = True
        scheduler.addItem(device_id,SPEED[room.device.speed])
        
    elif command == "turn_off":
        room.device.working = False
        scheduler.RemoveItem(device_id)

    elif command == "set_temperature":
        room.device.target_temperature = args

    elif command == "set_speed":
        room.device.speed = args
        scheduler.RemoveItem(device_id)
        scheduler.addItem(device_id,SPEED[room.device.speed])
        
    #hotel.updatedevice(DeviceStatus(**new_state))
    # TODO:产生一条详单记录 Logentry
    return {"status":"success!"}

@app.post('/admin_control')
async def admin_control(body=Body(None)):
    # turn_on, turn_off, set_mode, set_valid_range, set_price
    command, args = body["command"], body["args"]

    if command == "turn_on":
        hotel.central.isopen = True
    elif command == "turn_off":
        hotel.central.isopen = False
        hotel.central.scheduler.clear()
        for k, v in hotel.rooms.items():
            v.device.working = False
    elif command == "set_mode":
        hotel.central.mode = args
    #TODO
    elif command == "set_valid_range":
        hotel.central.limit = args
        for k, v in hotel.rooms.items():
            past_temp = v.device.target_temperature
            v.device.target_temperature = max(args[0],past_temp)
            v.device.target_temperature = min(args[1],v.device.target_temperature)
    #TODO
    elif command == "set_price":
        hotel.central.cost = args
        #TODO

    return {"status":"success!"}

@app.get('/get_all_device_status')
async def get_all_device_status():
    return [hotel.getroomstate(key).__dict__ for key, value in hotel.rooms.items()]

@app.get('/get_device_status')
async def get_device_status(device_id):
    return hotel.getroomstate(device_id).__dict__

@app.post('/check_in')
async def check_in(room_id, body=Body(None)):
    guest_name = body["guest_name"]

    if not hotel.rooms[room_id].isused:
        room = hotel.rooms[room_id]
        room.isused = True
        room.checkin = datetime.now()
        room.username = guest_name
        room.device = DeviceStatus(False,False,24,DEFAULT_TARGET_TEMP,'mid',0)
        
        #hotel.updateroom(newstate)
        # TODO:产生一条详单记录 Logentry
    
    return {"status":"success!"}

@app.post('/check_out')
async def check_out(room_id, body=Body(None)):

    guest_name = body["guest_name"]
    if not hotel.rooms[room_id].isused:
        room = hotel.rooms[room_id]
        room.isused = False
        room.checkout = datetime.now()
        room.username = ''
        room.device = DeviceStatus(False,False,24,DEFAULT_TARGET_TEMP,'mid',0)
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

    pass

@app.get('/bill_detail')
async def get_log(guest_name):
    """
    返回某个房间的详单
    """
    check_in_t, check_out_t = hotel.rooms[room_id].check_in_time, hotel.rooms[room_id].check_out_time
    res = Export_room_log(room_id,check_in_t,check_out_t)
    return res

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