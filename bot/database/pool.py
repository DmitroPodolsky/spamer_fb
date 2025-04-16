import aiosqlite
from loguru import logger
# from bot.config import settings


async def get_conn() -> aiosqlite.Connection:
    """Получить асинхронное соединение с SQLite"""
    conn = await aiosqlite.connect("data/ha.db")
    conn.row_factory = aiosqlite.Row 
    return conn

async def release_conn(conn: aiosqlite.Connection) -> bool:
    try:
        await conn.commit()
        await conn.close()
        return True
    except Exception as e:
        logger.error(f"Error closing SQLite connection: {e}")
        return False