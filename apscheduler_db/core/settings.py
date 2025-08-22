from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    scheduler_app_name: str = "DefaultAppTask"
    scheduler_table_name: str = "scheduler_jobs"
    scheduler_logger_path: str = "logs"
    scheduler_logger_name_prefix: str = "scheduler_app"
    scheduler_mysqldb_url: str
    scheduler_redisdb_url: str

    scheduler_default_misfire_grace_time: int = 3600    # 允许任务延迟执行的最大时间（单位：秒）
    scheduler_default_coalesce: bool = True             # 合并任务
    scheduler_default_replace_existing: bool = False    # 替换已存在任务
    scheduler_default_timezone: str = "Asia/Shanghai" # 时区
    scheduler_default_max_instances: int = 1 # 最大实例数
    scheduler_default_thread: int = 30 # 线程数
    scheduler_default_process: int = 10
    scheduler_openapi_url: str = "/openapi.json"

    @property
    def get_redis_perfix(self):
        return f"{self.scheduler_app_name}:scheduler"

    class Config:
        env_file = ".env"
        # env_prefix = "SCHEDULER_"
        extra = "allow"

@lru_cache
def get_settings():
    return Settings()