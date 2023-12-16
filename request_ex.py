import request_ex
import time

base_url = "http://localhost:8080"  # 请根据你的FastAPI应用的实际地址进行修改

# 0s时启动空调系统
request_ex.post(f"{base_url}/admin_control", json={"command": "turn_on", "args": {}})
time.sleep(10)

# 10s时启动房间1
request_ex.post(f"{base_url}/remote_control", json={"device_id": 1, "command": "turn_on", "args": {}})
time.sleep(10)

# 20s时设置房间1为24度
request_ex.post(f"{base_url}/remote_control", json={"device_id": 1, "command": "set_temperature", "args": {"target_temp": 24}})
time.sleep(10)

# 启动房间2
request_ex.post(f"{base_url}/remote_control", json={"device_id": 2, "command": "turn_on", "args": {}})

# 30s时启动房间3
time.sleep(10)
request_ex.post(f"{base_url}/remote_control", json={"device_id": 3, "command": "turn_on", "args": {}})

# 40s时房间2设置为25度
time.sleep(10)
request_ex.post(f"{base_url}/remote_control", json={"device_id": 2, "command": "set_temperature", "args": {"target_temp": 25}})

# 40s时房间4，房间5开机
request_ex.post(f"{base_url}/remote_control", json={"device_id": 4, "command": "turn_on", "args": {}})
request_ex.post(f"{base_url}/remote_control", json={"device_id": 5, "command": "turn_on", "args": {}})

# 50s时房间3设置为27度
time.sleep(10)
request_ex.post(f"{base_url}/remote_control", json={"device_id": 3, "command": "set_temperature", "args": {"target_temp": 27}})

# 50s时房间5设置为高风速
request_ex.post(f"{base_url}/remote_control", json={"device_id": 5, "command": "set_speed", "args": {"speed": "high"}})

# 60s时房间1设置为高风速
time.sleep(10)
request_ex.post(f"{base_url}/remote_control", json={"device_id": 1, "command": "set_speed", "args": {"speed": "high"}})

# 80s时房间5设置为24度
time.sleep(20)
request_ex.post(f"{base_url}/remote_control", json={"device_id": 5, "command": "set_temperature", "args": {"target_temp": 24}})

# 100s时设置房间1为28度，设置房间4为28度，风速为高
time.sleep(20)
request_ex.post(f"{base_url}/remote_control", json={"device_id": 1, "command": "set_temperature", "args": {"target_temp": 28}})
request_ex.post(f"{base_url}/remote_control", json={"device_id": 4, "command": "set_temperature", "args": {"target_temp": 28}})
request_ex.post(f"{base_url}/remote_control", json={"device_id": 4, "command": "set_speed", "args": {"speed": "high"}})

# 120s时设置房间5为中风速
time.sleep(20)
request_ex.post(f"{base_url}/remote_control", json={"device_id": 5, "command": "set_speed", "args": {"speed": "mid"}})

# 130s时设置房间2为高风速
time.sleep(10)
request_ex.post(f"{base_url}/remote_control", json={"device_id": 2, "command": "set_speed", "args": {"speed": "high"}})

# 150s时房间1关机，房间3设置为低风速
time.sleep(20)
request_ex.post(f"{base_url}/remote_control", json={"device_id": 1, "command": "turn_off", "args": {}})
request_ex.post(f"{base_url}/remote_control", json={"device_id": 3, "command": "set_speed", "args": {"speed": "low"}})

# 170s时设置房间5关机
time.sleep(20)
request_ex.post(f"{base_url}/remote_control", json={"device_id": 5, "command": "turn_off", "args": {}})

# 180s时设置房间3为高风速
time.sleep(10)
request_ex.post(f"{base_url}/remote_control", json={"device_id": 3, "command": "set_speed", "args": {"speed": "high"}})

# 190s时设置房间1开机，设置房间4为25度，风速为中
time.sleep(10)
request_ex.post(f"{base_url}/remote_control", json={"device_id": 1, "command": "turn_on", "args": {}})
request_ex.post(f"{base_url}/remote_control", json={"device_id": 4, "command": "set_temperature", "args": {"target_temp": 25}})
request_ex.post(f"{base_url}/remote_control", json={"device_id": 4, "command": "set_speed", "args": {"speed": "mid"}})

# 210s时设置房间2为27度，风速为中，房间5开机
time.sleep(20)
request_ex.post(f"{base_url}/remote_control", json={"device_id": 2, "command": "set_temperature", "args": {"target_temp": 27}})
request_ex.post(f"{base_url}/remote_control", json={"device_id": 2, "command": "set_speed", "args": {"speed": "mid"}})
request_ex.post(f"{base_url}/remote_control", json={"device_id": 5, "command": "turn_on", "args": {}})

# 250s时设置房间1，3，5关机
time.sleep(40)
request_ex.post(f"{base_url}/remote_control", json={"device_id": 1, "command": "turn_off", "args": {}})
request_ex.post(f"{base_url}/remote_control", json={"device_id": 3, "command": "turn_off", "args": {}})
request_ex.post(f"{base_url}/remote_control", json={"device_id": 5, "command": "turn_off", "args": {}})

# 260s时设置房间2，4关机
time.sleep(10)
request_ex.post(f"{base_url}/remote_control", json={"device_id": 2, "command": "turn_off", "args": {}})
request_ex.post(f"{base_url}/remote_control", json={"device_id": 4, "command": "turn_off", "args": {}})