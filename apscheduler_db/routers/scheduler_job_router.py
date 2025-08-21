from fastapi import APIRouter, Query
from typing import Union, Optional

from apscheduler_db.core import manage_task
import apscheduler_db.services.scheduler_job_service as sts
from apscheduler_db.dtos import scheduler_job_dto
from apscheduler_db.models import scheduler_job_model

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


@router.get("/get_scheduler", response_model=list[scheduler_job_dto.JobInfoDTO], description="获取当前调度器实例")
def get_scheduler():
    """
    获取当前的调度器实例
    """
    return sts.query_jobs(manage_task.scheduler)

@router.put("/job_state/{job_id}/{state}", description="暂停/启动指定的调度任务")
async def update_job_state(job_id: str, state: int):
    """
    更新指定调度任务的状态（暂停或启动）
    """
    return await sts.update_job_info(manage_task.scheduler, scheduler_job_dto.ModifyJobDTO(func_id=job_id, valid=state))

@router.post("/modify_job", response_model=scheduler_job_dto.JobInfoDTO, description="修改调度任务")
async def modify_job(job_data: scheduler_job_dto.ModifyJobDTO):
    return await sts.update_job_info(manage_task.scheduler, job_data)

@router.post("/add_job", response_model=scheduler_job_dto.JobInfoDbDTO, description="添加调度任务")
async def add_job(job_data: scheduler_job_dto.CreateJobDTO):
    """
    添加新的调度任务
    """
    return await sts.add_job(manage_task.scheduler, scheduler_job_model.SchedulerJob(**job_data.model_dump(exclude_none=True, exclude_unset=True)))

@router.get("/query_jobs", response_model=list[scheduler_job_dto.JobInfoDbDTO], description="查询所有调度任务")
async def query_jobs(valids: Optional[Union[list[int], int]] = Query(default=[0, 1])):
    __valids__ = valids
    if type(valids) is int:
        __valids__ = [valids]
    jobs = await sts.list_dbjobs(__valids__)
    return [scheduler_job_dto.JobInfoDbDTO.model_validate(job.model_dump()) for job in jobs]