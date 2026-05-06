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
        
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS clans (
            id SERIAL PRIMARY KEY,
            public_id BIGINT UNIQUE,
            name TEXT,
            owner_id BIGINT,
            owner_name TEXT
        );
        """)

        await conn.execute("""
        CREATE TABLE IF NOT EXISTS clan_requests (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            username TEXT,
            clan_id BIGINT,
            status TEXT DEFAULT 'pending'
        );
        """)

        await conn.execute("""
        CREATE TABLE IF NOT EXISTS clan_members (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            username TEXT,
            clan_id BIGINT,
            role TEXT DEFAULT 'member',
            dkp INTEGER DEFAULT 0
        );
        """)


def get_pool():
    if pool is None:
        raise RuntimeError("DB is not initialized")
    return pool

