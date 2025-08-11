from sqlmodel import select, update, insert

from core.database import get_db_session
from models.scheduler_logger_model import SchedulerLogger

async def add_log(log: SchedulerLogger):
    '''
    新增日志
    '''
    async with get_db_session() as db:
        save_sql = insert(SchedulerLogger).values(**log.model_dump())
        await db.execute(save_sql)
        await db.commit()

