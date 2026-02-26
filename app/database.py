import asyncpg
from .config import settings
from contextlib import asynccontextmanager
import logging
import aiofiles
import time

# Настройки БД

connection_pool = None
logger = logging.getLogger(__name__)

# Инициализация пула подключений к БД
async def init_pool():    
    global connection_pool
    attempt = 1
    while attempt < settings.MAX_ATTEMPT:
        try:
            connection_pool = await asyncpg.create_pool(
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                database=settings.POSTGRES_DB,
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                min_size=settings.POOL_MIN_CONN,
                max_size=settings.POOL_MAX_CONN,
            )
            break
        except Exception as error:
            logging.info("Ожидание базы данных...")
            time.sleep(settings.TIMEOUT)
    else:
        logging.error("Ошибка при инициализации пула подключений")

# Функция получения подключения
@asynccontextmanager
async def get_connect():
    if connection_pool is None:
        await init_pool()
        await init_database()
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

# Облагораживание БД через SQL-скрипты
async def init_database():
    try:
        async with get_connect() as connect:
            async with aiofiles.open("sql/init_db.sql", 'r') as file:
                sql = await file.read()
            await connect.execute(sql)
            logger.info("Добавлены таблицы")

            async with aiofiles.open("sql/api.sql", 'r') as file:
                sql = await file.read()
            await connect.execute(sql)
            logger.info("Добавлены функции")

    except Exception as error:
        logger.exception(f"Ошибка инициализации базы данных: {error}")
    
    
    
