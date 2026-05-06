# from db import cursor, conn
from db import pool, get_pool
import random

# CLANS
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


def get_clan_by_id(clan_id: int):
    return {"ok": False}
    # cursor.execute(
    #     "SELECT id, public_id, name FROM clans WHERE id = ?", 
    #     (clan_id,)
    # )
    # return cursor.fetchone()

def get_clan_by_public_id(public_id: int):
    return {"ok": False}
    # cursor.execute(
    #     "SELECT id, public_id, name FROM clans WHERE public_id = ?",
    #     (public_id,)
    # )
    # return cursor.fetchone()

def get_clan_members(clan_id: int):
    return {"ok": False}
    # cursor.execute("""
    #     SELECT cm.user_id, cm.username, cm.role, cm.dkp
    #     FROM clan_members cm
    #     join clans c ON c.id = cm.clan_id
    #     WHERE c.public_id = ?
    # """, (clan_id,))
    # return cursor.fetchall()

def remove_member_from_clan(clan_id: int, user_id: int):
    return {"ok": False}
    # cursor.execute("""
    #     DELETE FROM clan_members
    #     WHERE clan_id = ? AND user_id = ?
    # """, (clan_id, user_id))
    # conn.commit()


def is_user_in_clan(user_id: int, clan_id: int):
    return {"ok": False}
    # cursor.execute("""
    #     SELECT 1 FROM clan_members
    #     WHERE user_id = ? AND clan_id = ?
    # """, (user_id, clan_id))

    # return cursor.fetchone() is not None

def delete_clan_by_public_id(public_id: int):
    return {"ok": False}
    # 1. получаем внутренний id
    # cursor.execute(
    #     "SELECT id FROM clans WHERE public_id = ?",
    #     (public_id,)
    # )
    # clan = cursor.fetchone()

    # if not clan:
    #     return False

    # clan_id = clan[0]

    # # 2. удаляем всё связанное
    # cursor.execute("DELETE FROM clan_requests WHERE clan_id = ?", (clan_id,))
    # cursor.execute("DELETE FROM clan_members WHERE clan_id = ?", (clan_id,))
    # cursor.execute("DELETE FROM clans WHERE id = ?", (clan_id,))

    # conn.commit()
    # return True



def leave_clan(clan_id: int, user_id: int):
    return {"ok": False}
    # cursor.execute("""
    #     DELETE FROM clan_members
    #     WHERE clan_id = ? AND user_id = ?
    # """, (clan_id, user_id))

    # conn.commit()

def update_member_role(clan_id: int, user_id: int, role: str):
    return {"ok": False}
    # cursor.execute("""
    #     UPDATE clan_members
    #     SET role = ?
    #     WHERE clan_id = ? AND user_id = ?
    # """, (role, clan_id, user_id))
    # conn.commit()


# Ивенты и ДКП
def update_member_dkp(clan_id: int, user_id: int, new_dkp: int):
    return {"ok": False}
    # cursor.execute("""
    #     UPDATE clan_members
    #     SET dkp = ?
    #     WHERE clan_id = ? AND user_id = ?
    # """, (new_dkp, clan_id, user_id))
    # conn.commit()


# REQUESTS
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

def get_pending_requests_for_clans(clan_ids: list):
    return {"ok": False}
    # query = f"""
    #     SELECT cr.id, cr.user_id, cr.username, c.name
    #     FROM clan_requests cr
    #     JOIN clans c ON c.id = cr.clan_id
    #     WHERE cr.clan_id IN ({','.join(['?']*len(clan_ids))})
    #     AND cr.status = 'pending'
    # """

    # cursor.execute(query, clan_ids)
    # return cursor.fetchall()


def get_request_by_id(request_id: int):
    return {"ok": False}
    # cursor.execute("""
    #     SELECT id, user_id, username, clan_id, status
    #     FROM clan_requests
    #     WHERE id = ?
    # """, (request_id,))

    # return cursor.fetchone()



def accept_request(request_id: int, user_id: int, username: str, clan_id: int):
    return {"ok": False}
    # добавляем в клан
    # cursor.execute("""
    #     INSERT INTO clan_members (user_id, username, clan_id, role, dkp)
    #     VALUES (?, ?, ?, 'member', 0)
    # """, (user_id, username, clan_id))

    # # обновляем статус
    # cursor.execute("""
    #     UPDATE clan_requests
    #     SET status = 'accepted'
    #     WHERE id = ?
    # """, (request_id,))

    # conn.commit()

def reject_request(request_id: int):
    return {"ok": False}
    # cursor.execute("""
    #     UPDATE clan_requests
    #     SET status = 'rejected'
    #     WHERE id = ?
    # """, (request_id,))

    # conn.commit()


def has_pending_request(user_id: int, clan_id: int):
    return {"ok": False}
    # cursor.execute("""
    #     SELECT 1 FROM clan_requests
    #     WHERE user_id = ? AND clan_id = ? AND status = 'pending'
    # """, (user_id, clan_id))

    # return cursor.fetchone() is not None

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



# OTHER
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