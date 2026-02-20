import asyncpg
from app.config import settings
from contextlib import asynccontextmanager
import logging

# Настройки подключения к БД

connection_pool = None
logger = logging.getLogger(__name__)

# Инициализация пула подключений к БД
async def init_pool():
    global connection_pool
    try:
        connection_pool = await asyncpg.create_pool(
            user=settings.USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            min_size=settings.POOL_MIN_CONN,
            max_size=settings.POOL_MAX_CONN,
        )
    except Exception as error:
        logging.exception("Ошибка при инициализации пула подключений")
        raise

# Функция получения подключения
@asynccontextmanager
async def get_connect():
    if connection_pool is None:
        await init_pool()
    connection = await connection_pool.acquire()
    logger.debug("Аренда подключения из пула")

    try:
        yield connection
    finally:
        await connection_pool.release(connection)
        logger.debug("Возврат подключения в пул")

# Закрытие пула подключений к БД
async def close_connection_pool():
    if connection_pool:
        await connection_pool.close()
