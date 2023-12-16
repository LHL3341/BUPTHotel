import requests
import json
import time

base_url = 'http://127.0.0.1:10086'
# Flask应用的URL（假设运行在本地端口5000上）

# 定义一个函数来发送请求
def send_command_admin(command, args={}):
    url = f"{base_url}/admin_control"
    # 构造请求的数据
    data = {
        "command": command,
        "args": args
    }
    # 发送POST请求
    response = requests.post(url, json=data)
    return response # 返回响应的JSON数据

# 示例命令


# 定义一个函数来发送请求
def send_command_turn_on(device_id, command, args=None):
    url = f"{base_url}/remote_control"
    if args is None:
        args = {}
    # 构造请求的数据
    params = {"device_id": device_id}
    data = {"command": command, "args": args}

    # 发送POST请求
    response = requests.post(url, params=params, json=data)
    return response.json()  # 返回响应的JSON数据


# 定义一个函数来发送请求
def check_in(room_id, guest_name):
    url = f"{base_url}/check_in"
    # 构造请求的数据
    params = {"room_id": room_id} # URL查询参数
    data = {"guest_name": guest_name} # JSON数据

    # 发送POST请求
    response = requests.post(url, params=params, json=data)
    return response.json()  # 返回响应的JSON数据
#print(send_command("101", "turn_on"))

# # # 关机【通过】
# print(send_command("1", "turn_off"))

# # 设置温度（例如设置为25，然后设置为比现在的温度低1度，特殊情况[通过]
# print(send_command("1", "set_temperature", {"target_temperature": 12}))

# # 设置风速（例如设置为2），先升高，后降低，一直调整温度设置[通过]
# print(send_command("1", "set_speed", {"speed": 3}))
request_cap = {}
if __name__ == "__main__":
    print(send_command_admin("set_mode", {"mode": 'warm'}))  # 制热

    # 设置有效温度范围（例如18到28度）
    print(send_command_admin("set_valid_range", {"valid_range_low":18,"valid_range_high":28}))

    # 设置费率（例如费率为2）
    print(send_command_admin("set_rate", {"fee_rate":[1]}))

    print(send_command_admin("turn_on"))
    print("管理员进行了开机设置，且开机设置成功！")

    #### 用户进行入住
    print(check_in("101", "109c"))
    print("用户109c进行了入住，且入住成功！")
    print(check_in("102", "111a"))
    print("用户111a进行了入住，且入住成功！")
    print(check_in("103", "112b"))
    print("用户112b进行了入住，且入住成功！")
    print(check_in("104", "112g"))
    print("用户112g进行了入住，且入住成功！")
    print(check_in("105", "113c"))
    start_time = time.time()
    time.sleep(10)

    count_time =0
    while True:
        end_time = time.time()
        if end_time - start_time > 10:
            print("时间片：",count_time)
            ###开始测试逻辑
            start_time = end_time
            if count_time == 0:
                print(send_command_turn_on("101", "turn_on"))
                time.sleep(10)
            elif count_time == 1:
                print(send_command_turn_on("101", "set_temperature", {"target_temp": 24}))
                print(send_command_turn_on("102", "turn_on"))
            elif count_time == 2:
                print(send_command_turn_on("103", "turn_on"))
            elif count_time == 3:
                print(send_command_turn_on("102", "set_temperature", {"target_temp": 25}))
                print(send_command_turn_on("104", "turn_on"))
                print(send_command_turn_on("105", "turn_on"))
            elif count_time == 4:
                print(send_command_turn_on("103", "set_temperature", {"target_temp": 27}))
                print(send_command_turn_on("105", "set_speed", {"speed": "high"}))
            elif count_time == 5:
                print(send_command_turn_on("105", "set_speed", {"speed": "high"}))
            elif count_time == 7:
                print(send_command_turn_on("105", "set_temperature", {"target_temp": 24}))
            elif count_time == 9:
                print(send_command_turn_on("101", "set_temperature", {"target_temp": 28}))
                print(send_command_turn_on("104", "set_temperature", {"target_temp": 24}))
                print(send_command_turn_on("104", "set_speed", {"speed": "high"}))
            elif count_time == 11:
                print(send_command_turn_on("105", "set_speed", {"speed": "mid"}))
            elif count_time == 12:
                print(send_command_turn_on("105", "set_speed", {"speed": "high"}))
            elif count_time == 14:
                print(send_command_turn_on("101", "turn_off"))
                print(send_command_turn_on("104", "set_speed", {"speed": "low"}))
            elif count_time == 16:
                print(send_command_turn_on("105", "turn_off"))
            elif count_time == 18:
                print(send_command_turn_on("103", "set_speed", {"speed": "high"}))
            elif count_time == 19:
                print(send_command_turn_on("101", "turn_on"))
                print(send_command_turn_on("104", "set_temperature", {"target_temp": 25}))
                print(send_command_turn_on("104", "set_speed", {"speed": "mid"}))
            elif count_time == 21:
                print(send_command_turn_on("102", "set_temperature", {"target_temp": 27}))
                print(send_command_turn_on("102", "set_speed", {"speed": "mid"}))
                print(send_command_turn_on("105", "turn_on"))
            elif count_time == 24:
                print(send_command_turn_on("101", "turn_off"))
                print(send_command_turn_on("103", "turn_off"))
                print(send_command_turn_on("105", "turn_off"))
            elif count_time == 25:
                print(send_command_turn_on("102", "turn_off"))
                print(send_command_turn_on("104", "turn_off"))

            count_time += 1

    ###开始进行事件的响应