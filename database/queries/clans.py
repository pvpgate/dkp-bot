from database.db import pool, get_pool
import random


# ------------------------------
# Кланы пользователя
# ------------------------------
async def get_user_clans(user_id: int):
    pool = get_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT c.id, c.public_id, c.name, cm.role, cm.dkp
            FROM clan_members cm
            JOIN clans c ON c.id = cm.clan_id
            WHERE cm.user_id = $1
        """, user_id)

    return rows

# ------------------------------
# Генерируем рандомный ID клана
# ------------------------------
def generate_clan_id():
    return random.randint(100000, 999999)

async def generate_unique_clan_id(conn):
    while True:
        clan_id = generate_clan_id()

        exists = await conn.fetchval(
            "SELECT 1 FROM clans WHERE public_id = $1",
            clan_id
        )

        if not exists:
            return clan_id

# ------------------------------
# Создание клана
# ------------------------------
async def create_clan_db(name: str, owner_id: int, owner_name: str):
    pool = get_pool()

    async with pool.acquire() as conn:

        # проверка имени
        existing = await conn.fetchrow(
            "SELECT id FROM clans WHERE LOWER(name) = LOWER($1)",
            name
        )

        if existing:
            return {"ok": False, "error": "CLAN_ALREADY_EXISTS"}

        # генерируем ID
        public_id = await generate_unique_clan_id(conn)

        # создаём клан
        clan = await conn.fetchrow(
            """
            INSERT INTO clans (name, owner_id, owner_name, public_id)
            VALUES ($1, $2, $3, $4)
            RETURNING id
            """,
            name, owner_id, owner_name, public_id
        )

        clan_id = clan["id"]

        # добавляем лидера
        await conn.execute(
            """
            INSERT INTO clan_members (user_id, username, clan_id, role, dkp)
            VALUES ($1, $2, $3, $4, $5)
            """,
            owner_id, owner_name, clan_id, "leader", 0
        )

        return {
            "ok": True,
            "clan_id": clan_id,
            "public_id": public_id,
            "name": name
        }