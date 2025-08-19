from apscheduler_db.core.loggin import logger

import apscheduler.events as events
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.executors.asyncio import AsyncIOExecutor
from fastapi import FastAPI

from apscheduler_db.services.scheduler_job_log_service import sync_add_log, run_clear_logs
from apscheduler_db.services.scheduler_job_service import run_db_task
from apscheduler_db.core.settings import get_settings
from apscheduler_db.models.scheduler_logger_model import SchedulerLogger

settings = get_settings()

scheduler: AsyncIOScheduler = None

job_configure = {
    'job_defaults': {
        'misfire_grace_time': settings.scheduler_default_misfire_grace_time,    # 默认容忍 1h延迟
        'coalesce': settings.scheduler_default_coalesce,                        # 合并错过的任务
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
    job_log = []

    if event.code == events.EVENT_JOB_SUBMITTED:
        logger.info(f"[任务开始] job_id={event.job_id}")
        for scheduled_run_time in event.scheduled_run_times:
            job_log.append(SchedulerLogger(job_id=event.job_id, event='JOB_SUBMITTED', scheduled_run_time=scheduled_run_time, message=f"[任务开始] job_id={event.job_id}"))
    elif event.code == events.EVENT_JOB_EXECUTED:
        logger.info(f"[任务完成] job_id={event.job_id}")
        job_log.append(SchedulerLogger(job_id=event.job_id, event='JOB_EXECUTED', scheduled_run_time=event.scheduled_run_time, message=f"[任务完成] job_id={event.job_id} | {event.traceback or event.exception}"))
    elif event.code == events.EVENT_JOB_ERROR:
        logger.error(f"[任务失败] job_id={event.job_id}|错误：{event.traceback or event.exception}")
        job_log.append(SchedulerLogger(job_id=event.job_id, event='JOB_ERROR', scheduled_run_time=event.scheduled_run_time, message=f"[任务失败] job_id={event.job_id} | {event.traceback or event.exception}"))
    elif event.code == events.EVENT_JOB_MISSED:
        logger.warning(f"[任务错过执行] job_id={event.job_id}")
        job_log.append(SchedulerLogger(job_id=event.job_id, event='JOB_MISSED', scheduled_run_time=event.scheduled_run_time, message=f"[任务错过执行] job_id={event.job_id}"))

    # if job_log:
    #     sync_add_log(job_log)


async def init_task(scheduler: AsyncIOScheduler):
    '''
    管理后台任务的任务
    '''

    # 初始化数据库任务
    await run_db_task(scheduler)

    # 每分钟根据数据库的任务配置刷新调度任务
    scheduler.add_job(run_db_task, trigger=IntervalTrigger(minutes=1, seconds=0), max_instances=1, kwargs={'scheduler': scheduler}, id='__run_db_task__')
    scheduler.add_job(run_clear_logs, trigger=IntervalTrigger(days=1, hours=2, minutes=0, seconds=0), max_instances=1, id='__run_clear_logs__')


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