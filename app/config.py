from pydantic_settings import BaseSettings
from pydantic import ConfigDict
import logging


# Общие настройки

class Settings(BaseSettings):
    PROJECT_NAME: str = "Аналитика успеваемости учеников"
    DESCRIPTION: str = """
        Небольшой REST-сервис на FastAPI для загрузки и анализа успеваемости студентов.

        Особенности:
        1. Принимает CSV-файлы и сохраняет данные в PostgreSQL.
        2. Выполняет валидацию данных.
        3. Предоставляет две аналитические ручки.
        4. Возвращает данные в формате JSON.
    """
    POSTGRES_DB: str
    DB_HOST: str
    DB_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POOL_MIN_CONN: int = 1          # Минимальное количество соединений с БД 
    POOL_MAX_CONN: int = 10         # Максимальное количество соединений с БД
    SIZE_BATCH: int = 1000          # Размер батча отметок, для которых в БД известны студенты
    SIZE_BATCH_NEW_STUD: int = 500  # Размер батча для неизвестных в БД студентов и их отметок
    LOG_LEVEL: int = logging.INFO
    MAX_ATTEMPT: int = 10           # Максимальное количество попыток создания пула 
    TIMEOUT: int = 2                # Время ожидания между попытками

    model_config = ConfigDict(env_file=".env")

settings = Settings()

