from dotenv import load_dotenv
load_dotenv()

import os
print(f"-----> load env: SCHEDULER_MYSQLDB_URL = [{os.getenv('SCHEDULER_MYSQLDB_URL')}]")
print(f"-----> load env: SCHEDULER_REDISDB_URL = [{os.getenv('SCHEDULER_REDISDB_URL')}]")

from apscheduler_db.core.loggin import logger

from fastapi import FastAPI
from contextlib import asynccontextmanager

from apscheduler_db.core.settings import get_settings
from apscheduler_db.core.database import init_db, create_db_and_tables
from apscheduler_db.core.cache import get_redis
from apscheduler_db.core import manage_task
from apscheduler_db.routers import scheduler_job_router

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 生命周期管理"""
    print("🚀 启动 FastAPI 服务，定时任务启动中...")

    try:
        init_db()
        await create_db_and_tables()
        logger.success('数据库初始化完成')
    except Exception as e:
        logger.error(e)
        raise Exception(e)

    app.__redisdb__ = await get_redis()
    app.__settings__ = settings

    await manage_task.start_scheduler(app)
    
    yield  # 允许 FastAPI 继续启动

    logger.info("🛑 FastAPI 关闭，定时任务停止...")

    await manage_task.close_scheduler(app)


app = FastAPI(
    description=f"{settings.scheduler_app_name}:调度模块",
    title=settings.scheduler_app_name,
    lifespan=lifespan
)

# 添加路由
app.include_router(scheduler_job_router.router)

