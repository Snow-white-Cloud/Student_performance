import logging
from app.config import settings

# Настройки логирования

def setup_logging_settings():
    logging.basicConfig(
        format="%(asctime)s: %(levelname)s в %(funcName)s произошло %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S",
        level=settings.LOG_LEVEL,
    )
    return logging.getLogger()
