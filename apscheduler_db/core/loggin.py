from loguru import logger
import logging
import os, sys
from pathlib import Path
from apscheduler_db.core.settings import get_settings

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

LOG_LEVEL_DICT = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}

_initialized = False

def init_logger():
    global _initialized
    if _initialized:
        return
    _initialized = True

    settings = get_settings()
    LOG_DIR = Path(settings.scheduler_logger_path or 'logs')
    LOG_DIR.mkdir(exist_ok=True)

    # 1. 配置 loguru 输出到控制台
    logger.remove()
    logger.add(
        sys.stdout,
        level=LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
    )

    # 2. 文件日志
    base_conf = {
        "level": LOG_LEVEL,
        "rotation": "10 MB",
        "retention": "10 days",
        "encoding": "utf-8"
    }
    logger.add(LOG_DIR / f"{settings.scheduler_logger_name_prefix}.log", **base_conf)
    logger.add(LOG_DIR / f"{settings.scheduler_logger_name_prefix}_sqlalchemy.log",
               format="{time} {level} {message}", filter="sqlalchemy", **base_conf)

    # 3. 日志拦截器（SQLAlchemy 等库）
    class DbInterceptHandler(logging.Handler):
        def emit(self, record):
            if record.levelno < LOG_LEVEL_DICT[LOG_LEVEL]:
                return
            logger.opt(depth=6).log(record.levelname, record.getMessage())

    for name in ("apscheduler_db", "sqlalchemy.engine", "sqlalchemy.pool",
                 "sqlalchemy.dialects", "sqlalchemy.engine.Engine"):
        logging.getLogger(name).setLevel(LOG_LEVEL_DICT[LOG_LEVEL])
        logging.getLogger(name).addHandler(DbInterceptHandler())

    # 4. 统一拦截其他标准 logging
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            if record.levelno < LOG_LEVEL_DICT[LOG_LEVEL]:
                return
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = "INFO"
            logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())

    logging.basicConfig(
        handlers=[InterceptHandler()],
        level=LOG_LEVEL_DICT[LOG_LEVEL],
        force=True
    )
