from database.db import pool, get_pool


# ----------------------------
# ЗАЯВКИ в клан (для лидеров)
# ----------------------------
async def get_clan_requests(clan_id: int):
    return await pool.fetch("""
        SELECT id, user_id, username, status
        FROM clan_requests
        WHERE clan_id = $1 AND status = 'pending'
    """, clan_id)


# ----------------------------
# Заявки пользователя
# ----------------------------
async def get_user_clan_requests(user_id: int):
    pool = get_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT c.name, c.public_id, cr.status
            FROM clan_requests cr
            JOIN clans c ON c.id = cr.clan_id
            WHERE cr.user_id = $1
        """, user_id)

    return rows


# ----------------------------
# Заявки пользователя
# ----------------------------
async def create_clan_request(user_id: int, username: str, public_id: int):
    pool = get_pool()

    async with pool.acquire() as conn:

        # 1. ищем клан
        clan = await conn.fetchrow(
            "SELECT id FROM clans WHERE public_id = $1",
            public_id
        )

        if not clan:
            return {"ok": False, "error": "CLAN_NOT_FOUND"}

        clan_id = clan["id"]

        # 2. проверяем: уже в ЭТОМ клане?
        in_this_clan = await conn.fetchrow(
            """
            SELECT 1 FROM clan_members
            WHERE user_id = $1 AND clan_id = $2
            """,
            user_id, clan_id
        )

        if in_this_clan:
            return {"ok": False, "error": "ALREADY_IN_THIS_CLAN"}

        # 3. проверяем: уже есть заявка именно в ЭТОТ клан?
        existing_request = await conn.fetchrow(
            """
            SELECT 1 FROM clan_requests
            WHERE user_id = $1 AND clan_id = $2 AND status = 'pending'
            """,
            user_id, clan_id
        )

        if existing_request:
            return {"ok": False, "error": "REQUEST_ALREADY_EXISTS"}

        # 4. создаём заявку
        await conn.execute(
            """
            INSERT INTO clan_requests (user_id, username, clan_id)
            VALUES ($1, $2, $3)
            """,
            user_id, username, clan_id
        )

        return {"ok": True}

# ----------------------------
# ПРИНЯТЬ заявку
# ----------------------------
async def accept_request(request_id: int):
    async with pool.acquire() as conn:

        req = await conn.fetchrow("""
            SELECT user_id, username, clan_id
            FROM clan_requests
            WHERE id = $1
        """, request_id)

        if not req:
            return {"ok": False, "error": "NOT_FOUND"}

        # обновляем статус заявки
        await conn.execute("""
            UPDATE clan_requests
            SET status = 'accepted'
            WHERE id = $1
        """, request_id)

        # добавляем в клан
        await conn.execute("""
            INSERT INTO clan_members (user_id, username, clan_id, role, dkp)
            VALUES ($1, $2, $3, 'member', 0)
        """, req["user_id"], req["username"], req["clan_id"])

        return {"ok": True}


# ----------------------------
# ОТКЛОНИТЬ заявку
# ----------------------------
async def reject_request(request_id: int):
    await pool.execute("""
        UPDATE clan_requests
        SET status = 'rejected'
        WHERE id = $1
    """, request_id)