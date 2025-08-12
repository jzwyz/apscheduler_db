from fastapi import APIRouter

from core import manage_task
import services.scheduler_job_service as sts

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
async def get_scheduler():
    """
    获取当前的调度器实例
    """
    return await sts.query_jobs(manage_task.scheduler)