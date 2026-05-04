from aiogram import Router, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
import random
from db import cursor, conn

router = Router()

def generate_clan_id():
    return random.randint(100000, 999999)  # 5-6 цифр

def generate_unique_clan_id():
    while True:
        clan_id = generate_clan_id()

        cursor.execute(
            "SELECT 1 FROM clans WHERE public_id = ?",
            (clan_id,)
        )

        if not cursor.fetchone():
            return clan_id


def create_clan(name: str, owner_id: int, owner_name: str):
    # 1. нормализуем имя
    name = name.strip()

    # 2. базовая валидация
    if len(name) < 3:
        return {
            "ok": False,
            "error": "CLAN_NAME_TOO_SHORT"
        }

    if len(name) > 16:
        return {
            "ok": False,
            "error": "CLAN_NAME_TOO_LONG"
        }

    # 2.1 проверка на допустимые символы
    if not name.isalnum():
        return {
            "ok": False,
            "error": "INVALID_CHARACTERS"
        }

    # 3. проверка на существующий клан
    cursor.execute(
        "SELECT id FROM clans WHERE name = ? COLLATE NOCASE",
        (name,)
    )
    existing = cursor.fetchone()

    if existing:
        return {
            "ok": False,
            "error": "CLAN_ALREADY_EXISTS"
        }


    # генерируем уникальный ID
    public_id = generate_unique_clan_id()

    # 4. создаём клан
    cursor.execute(
        "INSERT INTO clans (name, owner_id, owner_name, public_id) VALUES (?, ?, ?, ?)",
        (name, owner_id, owner_name, public_id)
    )

    clan_id = cursor.lastrowid

    # 5. добавляем лидера в участники
    cursor.execute(
        """
        INSERT INTO clan_members (user_id, username, clan_id, role, dkp)
        VALUES (?, ?, ?, ?, ?)
        """,
        (owner_id, owner_name, clan_id, "leader", 0)
    )

    # 6. сохраняем изменения
    conn.commit()

    # 7. успех
    return {
        "ok": True,
        "clan_id": clan_id,
        "public_id": public_id,
        "name": name
    }


class CreateClan(StatesGroup):
    waiting_for_name = State()

from aiogram.filters import Command

@router.message(Command("create_clan"))
async def start_create_clan_command(message: Message, state: FSMContext):
    await message.answer("Введите название клана:")
    await state.set_state(CreateClan.waiting_for_name)

@router.callback_query(lambda c: c.data == "create_clan")
async def start_create_clan(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название клана:")
    await state.set_state(CreateClan.waiting_for_name)

@router.message(CreateClan.waiting_for_name)
async def process_clan_name(message: types.Message, state: FSMContext):
    result = create_clan(
        name=message.text,
        owner_id=message.from_user.id,
        owner_name=message.from_user.username
    )

    if not result["ok"]:
        if result["error"] == "CLAN_ALREADY_EXISTS":
            await message.answer("❌ Клан с таким названием уже существует")
        elif result["error"] == "CLAN_NAME_TOO_SHORT":
            await message.answer("❌ Название слишком короткое (мин. 3 символа)")
        elif result["error"] == "CLAN_NAME_TOO_LONG":
            await message.answer("❌ Название слишком длинное (макс. 16 символов)")
        elif result["error"] == "INVALID_CHARACTERS":
            await message.answer("❌ Название может содержать только буквы и цифры (без пробелов)")
        return

    await message.answer(
        f"🎉 Клан '{result['name']}' создан!\nID: {result['public_id']}"
    )

    await state.clear()