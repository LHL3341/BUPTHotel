# BUPT-AirConditioner
## 克隆项目
```bash
git clone https://github.com/LHL3341/BUPT-AirConditioner.git
```
## 开发环境配置
```bash
conda create -n SE python=3.9
conda activate SE
pip install -r requirement.txt
```
## 项目结构
```
│  README.md
│  requirements.txt
│  utils.py
│
├─chatroom		#示例：局域网多人聊天室
├─Class-Manager #示例：课堂抬头率检测
│
├─Client
│  │  main.py   #可参考./chatroom/main.py
│  │  manager_air.py
│  │  manager_bill.py
│  │  user.py
│  │
│  └─ui #ui文件目录，同./Class-Manager/ui
│       __init__.py
│
└─Server
        backend.py #可参考./Class-Manager/backend/backend.py
        main.py #可参考./chatroom/server.py

```
## 启动服务器
1. 启动SQL数据库服务器
2. 在./Server下运行
    ```bash
    uvicorn main:app --host 127.0.0.1 --port 10086 --reload --log-level warning
    ```
## 启动客户端
运行
```bash
python Client/main.py
```
## 示例
关于ui设计、后端函数，可参考两个示例项目