from pydantic_settings import BaseSettings


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
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int
    USER: str
    DB_PASSWORD: str
    POOL_MIN_CONN: int = 1
    POOL_MAX_CONN: int = 10

    class Config:
        env_file = "db.env"

settings = Settings()

