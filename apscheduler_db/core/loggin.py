from loguru import logger
import logging
import os, sys
from pathlib import Path
from apscheduler_db.core.settings import get_settings

LOG_LEVEL = os.getenv('LOG_LEVEL', 'WARNING').upper()

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

    logger.remove()
    logger.add(
        sys.stdout,
        level=LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
    )

    base_conf = {
        "level": LOG_LEVEL,
        "rotation": "10 MB",
        "retention": "10 days",
        "encoding": "utf-8"
    }
    logger.add(LOG_DIR / f"{settings.scheduler_logger_name_prefix}.log", **base_conf)

    # 定义 loguru 拦截标准 logging 的 handler
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            try:
                level = logger.level(record.levelname).name
            except Exception:
                level = "INFO"
            logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())

    intercept_handler = InterceptHandler()

    # 清理 root logger 现有 handlers，只保留 intercept_handler
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(intercept_handler)
    root_logger.setLevel(LOG_LEVEL_DICT[LOG_LEVEL])
    root_logger.propagate = False

    for name in ("sqlalchemy.engine", "sqlalchemy.pool", "sqlalchemy.dialects", "sqlalchemy.engine.Engine"):
        _logging = logging.getLogger(name)
        _logging.setLevel(LOG_LEVEL_DICT[LOG_LEVEL])
        _logging.propagate = True  # 让日志向上传递
