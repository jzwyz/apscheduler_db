from core.loggin import logger

import apscheduler.events as events
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.executors.asyncio import AsyncIOExecutor
from fastapi import FastAPI
import time, math, datetime
import asyncio

from services.scheduler_job_log_service import save_job_log
from services.scheduler_job_service import run_db_task
from core.settings import get_settings
from models.scheduler_logger_model import SchedulerLogger

settings = get_settings()

scheduler: AsyncIOScheduler = None

job_configure = {
    'job_defaults': {
        'misfire_grace_time': settings.scheduler_default_misfire_grace_time,      # 默认容忍 1h延迟
        'coalesce': settings.scheduler_default_coalesce,                # 合并错过的任务
        'replace_existing': settings.scheduler_default_replace_existing,        # 允许替换存在的任务
        'timezone': settings.scheduler_default_timezone,
        'max_instances': settings.scheduler_default_max_instances
    },
    'executors': {
        'default': AsyncIOExecutor(),
        'thread': ThreadPoolExecutor(settings.scheduler_default_thread),
        'process': ProcessPoolExecutor(settings.scheduler_default_process)
    }
}

def job_listener(event):
    job_log = None
    if event.code == events.EVENT_JOB_SUBMITTED:
        logger.info(f"[任务开始] job_id={event.job_id}|job_name={event.job_name}")
        job_log = SchedulerLogger(job_id=event.job_id, event=event.code, event_time=event.scheduled_run_time, message=f"[任务开始] job_id={event.job_id}|job_name={event.job_name}")
    elif event.code == events.EVENT_JOB_EXECUTED:
        logger.info(f"[任务完成] job_id={event.job_id}|job_name={event.job_name} 运行耗时={event.scheduled_run_time} → {event.scheduled_run_time}")
        job_log = SchedulerLogger(job_id=event.job_id, event=event.code, event_time=event.scheduled_run_time, execution_time=event.execution_time, message=event.result)
    elif event.code == events.EVENT_JOB_ERROR:
        logger.error(f"[任务失败] job_id={event.job_id}|job_name={event.job_name} 错误：{event.exception}")
        job_log = SchedulerLogger(job_id=event.job_id, event=event.code, event_time=event.scheduled_run_time, execution_time=event.execution_time, message=event.exception)
    elif event.code == events.EVENT_JOB_MISSED:
        logger.warning(f"[任务错过执行] job_id={event.job_id}|job_name={event.job_name}")
        job_log = SchedulerLogger(job_id=event.job_id, event=event.code, event_time=event.scheduled_run_time, message="任务错过执行")
    
    if job_log:
        asyncio.create_task(save_job_log(job_log))


async def init_task(scheduler: AsyncIOScheduler):
    '''
    管理后台任务的任务
    '''

    # 初始化数据库任务
    await run_db_task(scheduler)

    # 每分钟根据数据库的任务配置刷新调度任务
    scheduler.add_job(run_db_task, trigger=IntervalTrigger(minutes=1), max_instances=1, kwargs={'scheduler': scheduler})


async def start_scheduler(app: FastAPI):
    global scheduler
    if scheduler is None:
        scheduler = AsyncIOScheduler(**job_configure)
        scheduler.add_listener(job_listener, events.EVENT_JOB_SUBMITTED | events.EVENT_JOB_EXECUTED | events.EVENT_JOB_ERROR | events.EVENT_JOB_MISSED)
        await init_task(scheduler)
        scheduler.start()
        app.__scheduler__ = scheduler
        logger.info("定时任务调度器已启动")
    else:
        logger.warning("调度器已存在，跳过初始化")

async def close_scheduler(app: FastAPI):
    if app and app.__scheduler__:
        app.__scheduler__.shutdown()


def demo_io_task():
    '''
    线程任务 demo
    app.tasks.manage_task#demo_io_task
    '''
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info("[线程任务] Start task (sleep 2s)... {}", now)
    time.sleep(10)
    logger.info("[线程任务] End task {}", now)

def demo_cpu_task():
    '''
    进程任务 demo
    app.tasks.manage_task#demo_cpu_task
    '''
    logger.info(f"[进程任务] Start CPU-intensive task")
    total = sum(math.sqrt(i) for i in range(10_000_000))
    logger.info(f"[进程任务] Done: total = {total}")