from fastapi import APIRouter, Depends

from apscheduler_db.core import manage_task
import apscheduler_db.services.scheduler_job_service as sts
from apscheduler_db.core.database import get_db_session, AsyncSession
from apscheduler_db.dtos import response_dto

router = APIRouter()

@router.get("/")
def root_path():
    return "Hello World"


@router.post("/run_job/{job_id}", description="立即运行指定的调度任务")
async def run_job(job_id: str, kwargs: dict = None):
    """
    手动触发指定调度任务执行（由调度器调度执行一次）
    """
    return await sts.run_job(manage_task.scheduler, job_id, kwargs)


@router.get("/get_scheduler")
def get_scheduler() -> list[response_dto.JobInfoDTO]:
    """
    获取当前的调度器实例
    """
    return sts.query_jobs(manage_task.scheduler)

@router.put("/job_state/{job_id}/{state}", description="暂停/启动指定的调度任务")
async def update_job_state(job_id: str, state: int):
    """
    更新指定调度任务的状态（暂停或启动）
    """
    return await sts.update_job_state(manage_task.scheduler, job_id, state)