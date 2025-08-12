from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timezone
from fastapi import Response
from sqlmodel import select, update

from apscheduler_db.core.database import get_db_session
from apscheduler_db.core.loggin import logger
from apscheduler_db.models.scheduler_job_model import SchedulerJob

def run_job_once(scheduler: AsyncIOScheduler, job_id, job, override_kwargs=None):
    '''
    立即运行一次指定的调度任务
    '''
    if not scheduler:
        raise RuntimeError("Scheduler is not initialized.")

    job_func = job.func
    job_args = job.args or []
    job_kwargs = job.kwargs.copy() if job.kwargs else {}

    if override_kwargs:
        job_kwargs.update(override_kwargs)

    # 立即运行一次（使用 DateTrigger）
    job_params = {
        'args': job_args,
        'kwargs': job_kwargs,
        'id': f"run_once_{job_id}_{datetime.now().timestamp()}",
        'name': f"手动运行【{job.name}】",
        'replace_existing': False
    }
    scheduler.add_job(**job_params, func=job_func, trigger=DateTrigger(run_date=datetime.now(timezone.utc)))
    return job_params


async def run_job(scheduler: AsyncIOScheduler, job_id: str, kwargs: dict):
    """
    手动触发指定调度任务执行（由调度器调度执行一次）
    """
    if not scheduler:
        raise RuntimeError("Scheduler is not initialized.")

    job = scheduler.get_job(job_id)
    if job:
        try:
            job_info = run_job_once(scheduler, job_id, job, kwargs)
            logger.debug(f"Job [{job.name}] scheduled to run immediately.")
            return Response(job_info, media_type='application/json')
        except Exception as e:
            logger.exception(f"Job {job_id} 调度触发失败: {e}")
            return Response({"job_id": job_id}, status_code=500, media_type='application/json')
    else:
        logger.error(f"Job {job_id} not found.")
        return Response({"job_id": job_id}, status_code=404, media_type='application/json')


async def query_jobs(scheduler: AsyncIOScheduler):
    """
    查询所有jobs
    """
    if not scheduler:
        raise RuntimeError("Scheduler is not initialized.")
    return Response([{ 'id': job.id, 'name': job.name,'next_run_time': job.next_run_time.strftime('%Y-%m-%d %H:%M:%S') } for job in scheduler.get_jobs()],
                    media_type='application/json')


async def list_dbjobs() -> list[SchedulerJob]:
    async with get_db_session() as db:
        exec = await db.execute(
            select(SchedulerJob).where(SchedulerJob.valid == 1)
        )
        return exec.scalars().all()


async def update_job(job: SchedulerJob):
    '''
    更新数据库记录
    '''
    if not job:
        return
    
    async with get_db_session() as db:
        update_query = update(SchedulerJob).where(SchedulerJob.id == job.id).values(**job.model_dump())
        await db.execute(update_query)
        await db.commit()


async def run_db_task(scheduler: AsyncIOScheduler):
    '''
    根据数据库中配置的任务初始化

    若任务不存在，新增
    若任务存在：
        任务发生更新，更新任务
        任务未发生更新，跳过
    '''
    
    try:
        jobs = await list_dbjobs()
        logger.debug('查询任务数量:{}',len(jobs))
        for job in jobs:
            try:

                if job.calculate_unique_key != job.unique_key:
                    await modify_job(scheduler, job, True)
                    logger.info('[{} - {}] | 任务发生变化，执行更新', job.func_id, job.name)
                    continue

                instance = scheduler.get_job(job.func_id)
                if not instance:
                    scheduler.add_job(**job.update_dict())
                    logger.success('启动任务:[{} - {}]成功 | trigger=[{}] | trigger_args=[{}]', job.func_id, job.name, job.trigger, job.trigger_args)
            except Exception as e:
                logger.error('任务更新/启动:[{} - {}]失败 | trigger=[{}] | trigger_args=[{}] | {}', job.func_id, job.name, job.trigger, job.trigger_args, str(e))
        logger.info('任务更新完成')
        if not jobs:
            logger.warning('没有任务更新完成')
    except Exception as e:
        logger.error(e)


async def modify_job(scheduler: AsyncIOScheduler, job: SchedulerJob, updated: bool = False):
    '''
    更新任务
    '''
    try:
        instance = scheduler.get_job(job.func_id)
        if instance:
            # 如果存在旧任务，则移除
            scheduler.remove_job(job_id=job.func_id)
        else:
            logger.warning('[{} - {}] | 任务不存在', job.func_id, job.name)

        # 状态为有效，新增新的任务
        if job.valid > 0:
            scheduler.add_job(**job.update_dict())        

        # 更新任务的 unique_key
        if updated:
            job.unique_key = job.calculate_unique_key
            await update_job(job)
        logger.info('[{} - {}] | 更新任务成功', job.func_id, job.name)
    except Exception as e:
        logger.error('[{} - {}] | 更新任务失败: [{}]', job.func_id, job.name, str(e))

    
