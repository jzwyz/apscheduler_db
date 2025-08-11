from typing import Optional
from sqlmodel import Field, SQLModel, Column, JSON, BigInteger, String, SMALLINT, Integer, TIMESTAMP
from sqlalchemy import func as sql_func, text
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from enum import Enum
import json, hashlib

from core.settings import get_settings
from utils import scheduler_util

setting = get_settings()

class SchedulerJob(SQLModel, table=True):
    __tablename__ = setting.scheduler_table_name
    __table_args__ = {'comment': '调度任务配置表'}

    id: int = Field(
        sa_column=Column(
            BigInteger,
            autoincrement=True,
            primary_key=True,
            comment="主键ID",
        )
    )

    func_id: str = Field(
        sa_column=Column(
            String(100),
            nullable=False,
            unique=True,
            comment="任务ID，唯一"
        )
    )

    func: str = Field(
        sa_column=Column(
            String(100),
            nullable=False,
            comment="调度任务执行的函数: app.tasks.request_amz#send_request_amz"
        )
    )

    name: str = Field(
        sa_column=Column(
            String(255),
            nullable=False,
            comment="任务名称"
        )
    )

    trigger: str = Field(
        default="date",
        sa_column=Column(
            String(20),
            nullable=False,
            server_default=text("'date'"),
            comment="任务触发方式: date/cron/interval"
        )
    )

    trigger_args: dict = Field(
        default={},
        sa_column=Column(
            JSON,
            nullable=False,
            comment="任务触发参数"
        )
    )

    args: list = Field(
        default=[],
        sa_column=Column(
            JSON,
            nullable=False,
            comment="数组形式的参数"
        )
    )

    kwargs: dict = Field(
        default={},
        sa_column=Column(
            JSON,
            nullable=False,
            comment="字典形式的参数"
        )
    )

    coalesce: bool = Field(
        default=True,
        sa_column=Column(
            SMALLINT,
            nullable=False,
            server_default=text("1"),
            comment="合并错过的任务"
        )
    )

    executor: str = Field(
        default="default",
        sa_column=Column(
            String(20),
            nullable=False,
            server_default=text("'default'"),
            comment="执行器：default/thread/process，默认使用线程池执行"
        )
    )

    replace_existing: bool = Field(
        default=False,
        sa_column=Column(
            SMALLINT,
            nullable=False,
            server_default=text("0"),
            comment="是否允许替换存在的任务"
        )
    )

    misfire_grace_time: int = Field(
        default=3600,
        sa_column=Column(
            Integer,
            nullable=False,
            server_default=text("3600"),
            comment="任务延迟容忍度，默认1小时，单位秒"
        )
    )

    max_instances: int = Field(
        default=1,
        sa_column=Column(
            Integer,
            nullable=False,
            server_default=text("1"),
            comment="最大实例数"
        )
    )

    timezone: str = Field(
        default="Asia/Shanghai",
        sa_column=Column(
            String(50),
            nullable=False,
            server_default=text("'Asia/Shanghai'"),
            comment="调度任务执行时区"
        )
    )

    user_id: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            nullable=True,
            comment="用户ID"
        )
    )

    valid: int = Field(
        default=0,
        sa_column=Column(
            SMALLINT,
            nullable=False,
            server_default=text("0"),
            comment="是否有效"
        )
    )

    unique_key: Optional[str] = Field(
        default=None,
        sa_column=Column(
            String(100),
            nullable=True,
            comment="计算任务参数的唯一标识"
        )
    )

    created_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=sql_func.current_timestamp(),
            comment="创建时间"
        )
    )

    updated_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=sql_func.current_timestamp(),
            server_onupdate=sql_func.current_timestamp(),
            comment="更新时间"
        )
    )

    # 计算唯一key的函数
    @property
    def calculate_unique_key(self) -> str:
        # 构建字典
        request_dict = self.model_dump(exclude=['created_at','updated_at','user_id','id'])

        # 对 headers, params 和 data 做排序，如果它们是 dict 类型
        for key in request_dict.keys():
            if isinstance(request_dict.get(key), Enum):
                # 如果 method 是枚举类型，转换为字符串
                request_dict[key] = request_dict[key].value
            elif isinstance(request_dict.get(key), dict):
                # 对字典中的字段进行排序
                request_dict[key] = dict(sorted(request_dict[key].items()))
        # 排序字典中的字段
        sorted_dict = {k: v for k, v in sorted(request_dict.items())}

        # 将排序后的字典转化为 JSON 字符串
        json_string = json.dumps(sorted_dict, separators=(",", ":"))

        # 使用 SHA256 生成哈希值
        unique_key = hashlib.sha256(json_string.encode("utf-8")).hexdigest()
        return unique_key


    def update_dict(self) -> dict:
        '''
        更新的内容
        '''
        __func__ = scheduler_util.import_function(self.func)
        return dict(
            id = self.func_id,
            name=self.name,
            func=__func__,
            trigger=self.trigger,
            args=self.args,
            kwargs=self.kwargs,
            coalesce=self.coalesce,
            executor=self.executor,
            replace_existing=self.replace_existing,
            misfire_grace_time=self.misfire_grace_time,
            max_instances=self.max_instances,
            timezone=self.timezone,
            next_run_time=(datetime.now(tz=ZoneInfo(self.timezone)) + timedelta(seconds=5)),
            **self.trigger_args
        )