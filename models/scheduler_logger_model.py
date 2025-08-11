from typing import Optional
from sqlmodel import Field, SQLModel, Column, JSON, BigInteger, String, SMALLINT, Integer, TIMESTAMP, Text, Float
from sqlalchemy import func as sql_func, text
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from enum import Enum
import json, hashlib

from core.settings import get_settings
from utils import scheduler_util

setting = get_settings()

class SchedulerLogger(SQLModel, table=True):
    __tablename__ = setting.scheduler_logger_table_name
    __table_args__ = {'comment': '调度日志表'}

    id: int = Field(sa_column=Column(BigInteger,autoincrement=True,primary_key=True,comment="主键ID"))
    job_id: str = Field(sa_column=Column(String(100),nullable=False,unique=True,comment="任务ID，唯一"))
    event: str = Field(sa_column=Column(String(20), nullable=False, comment="事件类型: job_executed/job_error/log_[info|error|waring|success]"))
    event_time: datetime = Field(sa_column=Column(TIMESTAMP, server_default=sql_func.now(), nullable=False, comment="事件发生时间"))
    execution_time: Optional[float] = Field(sa_column=Column(Float, nullable=True, comment="任务执行耗时（秒）"))
    message: str = Field(sa_column=Column(Text, nullable=False, comment="日志消息"))
    created_at: datetime = Field(sa_column=Column(TIMESTAMP, server_default=sql_func.now(), comment="创建时间"))
    updated_at: datetime = Field(sa_column=Column(TIMESTAMP, server_default=sql_func.current_timestamp(), server_onupdate=sql_func.current_timestamp(), comment="更新时间"))