from sqlmodel import insert, delete
from datetime import datetime, timedelta, timezone

from apscheduler_db.core.database import get_db_session, get_db_session_sync
import apscheduler_db.services.scheduler_job_service as sjs
from apscheduler_db.models.scheduler_logger_model import SchedulerLogger
from apscheduler_db.models.scheduler_job_model import SchedulerJob

def sync_add_log(log: list[SchedulerLogger]):
    """新增日志（同步 insert 写法）"""
    with get_db_session_sync() as db:
        for item in log:
            stmt = insert(SchedulerLogger).values(**item.model_dump())
            db.execute(stmt)
        db.commit()

async def run_clear_logs():
    '''
    清空日志
    '''

    jobs = await sjs.list_dbjobs()
    job_ids = [job.func_id for job in jobs]

    async with get_db_session() as db:

        # 根据任务删除 log_storage_days 范围外的日志
        for job in jobs:
            delete_sql = delete(SchedulerLogger).where(
                SchedulerLogger.job_id == job.func_id,
                SchedulerLogger.created_at < (datetime.now(timezone.utc) - timedelta(days=job.log_storage_days or 7))
            )
            await db.execute(delete_sql)

        # 删除所有 不在当前任务列表的历史日志
        delete_sql_all = delete(SchedulerLogger).where(
            SchedulerLogger.job_id.not_in_(job_ids),
            SchedulerLogger.created_at < (datetime.now(timezone.utc) - timedelta(days=job.log_storage_days or 7))
        )
        await db.execute(delete_sql_all)
        
        await db.commit()