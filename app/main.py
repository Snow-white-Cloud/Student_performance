from fastapi import FastAPI
from app.config import settings
from app.database import init_pool, close_connection_pool
from app.routers.get import router as router_get
from app.routers.upload import router as router_upload
from app.logger_config import setup_logging_settings


logger = setup_logging_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    docs_url="/swagger",
)

# Действие при запуске сервера: инициализация пула подключений
@app.on_event("startup")
async def startup():
    logger.info("Запуск сервера: инициализация пула подключений к БД")
    await init_pool()
    logger.info("Пул успешно создан")

# Действие при закрытии сервиса: закрытие пула подключений
@app.on_event("shutdown")
async def shutdown():
    logger.info("Остановка сервера: закрытие пула подключений к БД")
    await close_connection_pool()
    logger.info("Закрытие")

# На случай попадания в корневую страницу
@app.get("/")
async def root():
    return {"message": """
        Добро пожаловать!\n
        Для документации проследуйте в /swagger\n
        Для проверки выполнения задания в соответствующие /more-than-3-twos, /less-than-5-twos и /upload-grades\n
        А для хорошего настроения желаю солнышка за окном!    
    """}

# Подключение роутеров
app.include_router(router_get)
app.include_router(router_upload)