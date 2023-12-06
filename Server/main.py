import os
import sys
sys.path.append(os.path.abspath('..'))
sys.path.append(os.path.abspath('.'))
from fastapi import FastAPI, Body
from entity import *
from copy import deepcopy
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler

DEFAULT_TARGET_TEMP = 22
TIMESLICE = 30
FREQ = 1
DEFAULT_CHECKOUT = datetime(2035,1,1)
SPEED = {'low':0,'mid':1,'high':2}
WINDSPEED = {'low':1/3,'mid':0.5,'high':1}

class Room:
    #房间
    def __init__(self,id):
        self.roomid = id
        self.isused = False
        self.default_tmp = 25
        self.checkin = datetime.now()
        self.checkout = DEFAULT_CHECKOUT
        self.username = ''
        self.device = DeviceStatus(False,'warm',24,DEFAULT_TARGET_TEMP,'mid',0)

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
    start_tmp:float
    end_tmp:float
    cost:float
    
    def __init__(self, roomid,speed,start_tmp):
        self.request_time = datetime.now()
        self.roomid = roomid
        self.speed =speed
        self.start_time = None
        self.start_tmp = start_tmp
        self.served_time = 0
        self.cost =0

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
        return maxid
        
    def addItem(self,roomid,speed,env_tmp):
        # 收到新的请求
        item = Task(roomid,speed,env_tmp)
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
                room = hotel.rooms[roomid]
                device = room.device
                v.end_time = datetime.now()
                v.end_tmp = device.env_temperature
                break
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

    def Request(self,roomid,speed,env_tmp):
        item = Task(roomid,speed,env_tmp)
        self.wait_list[speed].append(item)        

    def clear(self):
        for k, v in self.wait_list.items():
            for i in v:
                self.RemoveItem(i.roomid)
        for k, v in self.serving_list.items():
            if v!=None:
                self.RemoveItem(v.roomid)
        self.wait_list = {0:[],1:[],2:[]}
        self.serving_list = {0:None,1:None,2:None}

class CentralAir:
    #空调配置
    def __init__(self):
        self.scheduler = Scheduler()
        self.isopen = True  #总开关
        self.cost = 1 #费率
        self.limit = [16,24]  #温度范围
        self.mode = 'warm'

class Hotel:
    #酒店
    def __init__(self):
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
                    scheduler.wait_list[v.speed].append(v)
                    scheduler.serving_list[k] = None
                    scheduler.Insert([v.speed])
        
    def schedule(self):
        room_ls = [self.scheduler.serving_list[i].roomid  for i in range(3) if self.scheduler.serving_list[i]!=None]
        for k, v in hotel.rooms.items():
            if v.device.room in room_ls and not v.device.is_on:
                v.device.is_on = True
                v.device.last_update = datetime.now()

            elif v.device.is_on and v.device.room not in room_ls:
                v.device.is_on = False
                # TODO:产生一条详单记录 Logentry
                v.device.last_update = datetime.now()

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
    timer.start()
    
@timer.scheduled_job('interval',seconds=FREQ)
async def timer_event():
    # 计费
    servelist = hotel.central.scheduler.serving_list
    cost = hotel.central.cost
    for k, v in servelist.items():
        if v != None:
            device = hotel.rooms[v.roomid].device
            device.total_cost += cost*WINDSPEED[device.speed]*(FREQ/60)
            v.cost += cost*WINDSPEED[device.speed]*(FREQ/60)
            v.served_time += FREQ
        
    # 调度
    hotel.Robin()

@timer.scheduled_job('interval',seconds=TIMESLICE)
async def update_temp():

    servelist = hotel.central.scheduler.serving_list
    waitlist = hotel.central.scheduler.wait_list
    served = [servelist[i].roomid for i in range(3) if servelist[i]!=None]
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
            slide = WINDSPEED[device.speed]
            if abs(device.target_temperature - device.env_temperature)<=slide:
                device.env_temperature = device.target_temperature
                # 释放资源
                print('释放',v.roomid)
                device.working = False
                hotel.central.scheduler.RemoveItem(v.roomid)
                
            elif device.env_temperature < device.target_temperature:
                device.env_temperature += slide
            else:
                device.env_temperature -= slide
    print("时间片",hotel.slice_num)
    hotel.slice_num +=1
    print("服务队列：",[servelist[i].roomid  for i in range(3) if servelist[i]!=None])
    print("等待队列：",[[room.roomid for room in waitlist[i]]  for i in range(3) if waitlist[i]!=None])



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
    # turn_on, turn_off, set_temperature, set_speed
    scheduler = hotel.central.scheduler
    command, args = body["command"], body["args"]
    room = hotel.rooms[device_id]
    if command == "turn_on":
        room.device.working = True
        scheduler.addItem(device_id,SPEED[room.device.speed],room.device.env_temperature)
        
    elif command == "turn_off":
        room.device.working = False
        scheduler.RemoveItem(device_id)

    elif command == "set_temperature":
        room.device.target_temperature = args["target_temp"]

    elif command == "set_speed":
        room.device.speed = args["speed"]
        scheduler.RemoveItem(device_id)
        scheduler.addItem(device_id,SPEED[room.device.speed],room.device.env_temperature)
        
    #hotel.updatedevice(DeviceStatus(**new_state))
    # TODO:产生一条详单记录 Logentry
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

    if command == "turn_on":
        hotel.central.isopen = True
    elif command == "turn_off":
        hotel.central.isopen = False
        hotel.central.scheduler.clear()
        for k, v in hotel.rooms.items():
            v.device.working = False
    elif command == "set_mode":
        hotel.central.mode = args["mode"]
    #TODO
    elif command == "set_valid_range":
        hotel.central.limit = args
        for k, v in hotel.rooms.items():
            past_temp = v.device.target_temperature
            v.device.target_temperature = max(args["valid_range_low"],past_temp)
            v.device.target_temperature = min(args["valid_range_high"],v.device.target_temperature)
    #TODO
    elif command == "set_price":
        hotel.central.cost = args["fee_rate"]
        #TODO

    return {"status":"success!"}

@app.get('/get_all_device_status')
async def get_all_device_status():
    res = []
    for key, value in hotel.rooms.items():
        dic = hotel.getroomstate(key).__dict__.copy()
        dic["room_id"] = key
        res.append(dic)
    return res

@app.get('/get_device_status')
async def get_device_status(device_id):
    return hotel.getroomstate(device_id).__dict__

@app.post('/check_in')
async def check_in(room_id, body=Body(None)):
    if room_id == '':
        return {"detail":"房间为空"}
    guest_name = body["guest_name"]

    if not hotel.rooms[room_id].isused:
        room = hotel.rooms[room_id]
        room.isused = True
        room.checkin = datetime.now()
        room.username = str(guest_name)
        print(room.username+'入住')
        #room.device = DeviceStatus(False,'warm',24,DEFAULT_TARGET_TEMP,'mid',0)
    
    return {"status":"success!"}

@app.post('/check_out')
async def check_out(room_id, body=Body(None)):

    guest_name = body["guest_name"]
    if not hotel.rooms[room_id].isused:
        room = hotel.rooms[room_id]
        room.isused = False
        room.checkout = DEFAULT_CHECKOUT
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
    for k,v in hotel.rooms.items():
        if v.username == guest_name:
            room = v
            res = Export_room_log(room.roomid,room.checkin,room.checkout)
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
            res = Export_room_log(room.roomid,room.checkin,room.checkout)
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
    