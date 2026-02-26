from fastapi import FastAPI
from .config import settings
from .database import init_pool, close_connection_pool, init_database
from .routers.get import router as router_get
from .routers.upload import router as router_upload
from .logger_config import setup_logging_settings
from contextlib import asynccontextmanager


logger = setup_logging_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Действие при запуске сервиса: инициализация пула подключений
    logger.info("Запуск сервера: инициализация пула подключений к БД")
    await init_pool()
    logger.info("Пул успешно создан. Запуск скриптов")
    await init_database()
    logger.info("Скрипты выполнены")

    yield

    # Действие при закрытии сервиса: закрытие пула подключений
    logger.info("Остановка сервера: закрытие пула подключений к БД")
    await close_connection_pool()
    logger.info("Закрытие")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    docs_url="/swagger",
    lifespan=lifespan
)
    
# На случай попадания в корневую страницу
@app.get("/")
async def root():
    return {"message": """
        Добро пожаловать! 
        Для документации проследуйте в /swagger 
        Для проверки выполнения задания в соответствующие /students/more-than-3-twos, /students/less-than-5-twos и /upload-grades 
        А для хорошего настроения желаю солнышка за окном!    
    """}

# Подключение роутеров
app.include_router(router_get)
app.include_router(router_upload)