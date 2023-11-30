from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from datetime import datetime
 
app = FastAPI()
 
# 创建一个scheduler实例
scheduler = AsyncIOScheduler()
 
# 每分钟执行的定时任务
@scheduler.scheduled_job('interval', seconds=1)
async def cron_job():
    # 执行任务的内容，例如打印当前时间
    print(f"The current time is {datetime.now()}")


scheduler.start()