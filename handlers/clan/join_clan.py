from aiogram import Router, types
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from database.db_queries import (
    get_clan_by_public_id,
    is_user_in_clan,
    has_pending_request,
    create_clan_request
)

router = Router()


# 🔹 FSM
class JoinClan(StatesGroup):
    waiting_for_clan_id = State()


# 🔘 КНОПКА
@router.callback_query(lambda c: c.data == "join_clan")
async def start_join(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите ID клана:")
    await state.set_state(JoinClan.waiting_for_clan_id)
    await callback.answer()


# 💬 КОМАНДА
@router.message(Command("join_clan"))
async def start_join_command(message: Message, state: FSMContext):
    await message.answer("Введите ID клана:")
    await state.set_state(JoinClan.waiting_for_clan_id)


# 🧠 ВВОД ID
@router.message(JoinClan.waiting_for_clan_id)
async def process_join(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введите числовой ID клана")
        return

    public_id = int(message.text)
    user_id = message.from_user.id
    username = message.from_user.username

    # 🔍 1. Проверка: существует ли клан
    clan = get_clan_by_public_id(public_id)

    if not clan:
        await message.answer("❌ Клан не найден")
        return

    clan_id, pid, clan_name = clan  # clan_id — внутренний id

    # 🚫 2. Уже в клане?
    if is_user_in_clan(user_id, clan_id):
        await message.answer("❌ Вы уже состоите в клане")
        return

    # 🚫 3. Уже есть заявка?
    if has_pending_request(user_id, clan_id):
        await message.answer("❌ Вы уже подали заявку в этот клан")
        return

    # ✅ 4. Создаём заявку
    create_clan_request(user_id, username, clan_id)

    await message.answer(
        f"📩 Заявка в клан '{clan_name}' отправлена!"
    )

    await state.clear()