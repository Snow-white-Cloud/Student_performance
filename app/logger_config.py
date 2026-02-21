import logging
from .config import settings

# Настройки логирования

def setup_logging_settings():
    logging.basicConfig(
        format="%(levelname)s: в %(funcName)s произошло %(message)s в %(asctime)s",
        datefmt="%d-%m-%Y %H:%M:%S",
        level=settings.LOG_LEVEL,
    )
    return logging.getLogger()
