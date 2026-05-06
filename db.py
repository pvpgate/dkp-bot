import os
import asyncpg

DATABASE_URL = os.getenv("DATABASE_URL")
pool = None

async def init_db():
    global pool

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set")

    pool = await asyncpg.create_pool(DATABASE_URL)

    async with pool.acquire() as conn:
        result = await conn.fetchval("SELECT 1")
        print("DB CONNECTED:", result)

def get_pool():
    if pool is None:
        raise RuntimeError("DB is not initialized")
    return pool