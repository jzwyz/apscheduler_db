from pydantic import BaseModel, Field
from typing import Optional

from datetime import datetime

class ModifyJobDTO(BaseModel):

    func_id: str = Field(description="任务ID，唯一")
    func: Optional[str] = Field(default=None, description="调度任务执行的函数: app.tasks.request_amz#send_request_amz")
    name: Optional[str] = Field(default=None, description="任务名称")
    trigger: Optional[str] = Field(default=None, description="任务触发方式: date/cron/interval")
    trigger_args: Optional[dict] = Field(default=None, description="任务触发参数")
    args: Optional[list] = Field(default=None, description="数组形式的参数")
    kwargs: Optional[dict] = Field(default=None, description="字典形式的参数")
    coalesce: Optional[int] = Field(default=None, description="合并错过的任务")
    executor: Optional[str] = Field(default=None, description="执行器：default/thread/process，默认使用线程池执行")
    replace_existing: Optional[int] = Field(default=None, description="是否允许替换存在的任务")
    misfire_grace_time: Optional[int] = Field(default=None, description="任务延迟容忍度，默认1小时，单位秒")
    max_instances: Optional[int] = Field(default=None, description="最大实例数")
    timezone: Optional[str] = Field(default=None, description="调度任务执行时区")
    valid: Optional[int] = Field(default=None, description="是否有效")
    log_storage_days: Optional[int] = Field(default=None, description="保留日志周期，默认7天，最长30天")

class JobInfoDTO(BaseModel):

    id: Optional[str] = Field(default=None, description='任务ID')
    name: Optional[str] = Field(default=None, description='任务名称')
    next_run_time: Optional[str] = Field(default=None, description='下次运行时间')
    executor: Optional[str] = Field(default=None, description='执行器')
    kwargs: Optional[dict] = Field(default=None, description='任务参数')
    args: Optional[list] = Field(default=None, description='任务位置参数')


class CreateJobDTO(BaseModel):
    func_id: str = Field(description="任务ID，唯一")
    func: str = Field(description="调度任务执行的函数: app.tasks.request_amz#send_request_amz")
    name: str = Field(description="任务名称")
    trigger: str = Field(description="任务触发方式: date/cron/interval")
    trigger_args: dict = Field(description="任务触发参数")
    args: Optional[list] = Field(default=[], description="数组形式的参数")
    kwargs: Optional[dict] = Field(default={}, description="字典形式的参数")
    coalesce: Optional[int] = Field(default=1, description="合并错过的任务")
    executor: Optional[str] = Field(default='default', description="执行器：default/thread/process，默认使用线程池执行")
    replace_existing: Optional[int] = Field(default=1, description="是否允许替换存在的任务")
    misfire_grace_time: Optional[int] = Field(default=30, description="任务延迟容忍度，默认1小时，单位秒")
    max_instances: Optional[int] = Field(default=1, description="最大实例数")
    timezone: Optional[str] = Field(default='Asia/Shanghai', description="调度任务执行时区")
    valid: Optional[int] = Field(default=1, description="是否有效", ge=0, le=1)
    log_storage_days: Optional[int] = Field(default=3, description="保留日志周期，默认7天，最长30天", ge=1, le=30)


class JobInfoDbDTO(BaseModel):
    id: Optional[int] = Field(description="主键ID")
    func_id: Optional[str] = Field(description="任务ID，唯一")
    func: Optional[str] = Field(description="调度任务执行的函数: app.tasks.request_amz#send_request_amz")
    name: Optional[str] = Field(description="任务名称")
    trigger: Optional[str] = Field(description="任务触发方式: date/cron/interval")
    trigger_args: Optional[dict] = Field(description="任务触发参数")
    args: Optional[list] = Field(description="数组形式的参数")
    kwargs: Optional[dict] = Field(description="字典形式的参数")
    coalesce: Optional[int] = Field(description="合并错过的任务")
    executor: Optional[str] = Field(description="执行器：default/thread/process，默认使用线程池执行")
    replace_existing: Optional[int] = Field(description="是否允许替换存在的任务")
    misfire_grace_time: Optional[int] = Field(description="任务延迟容忍度，默认1小时，单位秒")
    max_instances: Optional[int] = Field(description="最大实例数")
    timezone: Optional[str] = Field(description="调度任务执行时区")
    valid: Optional[int] = Field(description="是否有效")
    user_id: Optional[int] = Field(description="用户ID")
    unique_key: Optional[str] = Field(description="计算任务参数的唯一标识")
    log_storage_days: Optional[int] = Field(description="保留日志周期，默认7天，最长30天")
    created_at: Optional[datetime] = Field(description="创建时间")
    updated_at: Optional[datetime] = Field(description="更新时间")
