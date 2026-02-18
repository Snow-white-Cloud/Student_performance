import asyncpg
from app.config import settings
from contextlib import asynccontextmanager

connection_pool = None

async def init_pool():
    global connection_pool
    connection_pool = await asyncpg.create_pool(
        user=settings.USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        min_size=settings.POOL_MIN_CONN,
        max_size=settings.POOL_MAX_CONN,
    )

@asynccontextmanager
async def get_connect():
    if connection_pool is None:
        await init_pool()
    connection = await connection_pool.acquire()
    try:
        yield connection
    finally:
        await connection_pool.release(connection)

async def close_connection_pool():
    if connection_pool:
        await connection_pool.close()
