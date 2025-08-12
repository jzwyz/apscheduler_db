from pydantic import BaseModel, Field
from typing import Optional, Union

class JobInfoDTO(BaseModel):

    id: Optional[str] = Field(default=None, description='任务ID')
    name: Optional[str] = Field(default=None, description='任务名称')
    next_run_time: Optional[str] = Field(default=None, description='下次运行时间')
    executor: Optional[str] = Field(default=None, description='执行器')
    kwargs: Optional[dict] = Field(default=None, description='任务参数')
    args: Optional[list] = Field(default=None, description='任务位置参数')