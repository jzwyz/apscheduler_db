from loguru import logger
import logging
import os
from pathlib import Path

LOG_DIR = Path("logs")
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

LOG_LEVEL_DICT = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
}