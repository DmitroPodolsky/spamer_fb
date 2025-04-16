from loguru import logger
from bot.database.pool import get_conn, release_conn


async def execute_query(query: str, *args) -> int:
    conn = await get_conn()
    result = 0
    try:
        result = await conn.execute(query, *args)
    except Exception as e:
        logger.error(f"Error executing query: {e}")
    finally:
        await release_conn(conn)
    return result


async def fetch_query(query: str, *args):
    conn = await get_conn()
    try:
        async with conn.execute(query, *args) as cursor:
            result = await cursor.fetchall()
        return result
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        return []
    finally:
        await release_conn(conn)