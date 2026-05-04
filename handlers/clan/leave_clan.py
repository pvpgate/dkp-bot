from aiogram import Router, types
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from database.db_queries import (
    get_user_clans,
    get_clan_by_public_id,
    leave_clan
)

router = Router()


# 🔹 FSM
class LeaveClan(StatesGroup):
    waiting_for_clan_id = State()
    waiting_for_confirmation = State()


# Кнопка
@router.callback_query(lambda c: c.data == "leave_clan")
async def start_leave(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    clans = get_user_clans(user_id)

    if not clans:
        await callback.message.answer("❌ Вы не состоите ни в одном клане")
        await callback.answer()
        return

    text = "🏰 Твои кланы:\n\n"

    for clan_id, public_id, name, role, dkp in clans:
        role_emoji = "👑" if role == "leader" else "👤"
        text += f"{role_emoji} {name} (ID: {public_id})\n"

    text += "\nВведите ID клана, из которого хотите выйти:"

    await callback.message.answer(text)
    await state.set_state(LeaveClan.waiting_for_clan_id)
    await callback.answer()

# Команда
@router.message(Command("leave_clan"))
async def start_leave_command(message: Message, state: FSMContext):
    user_id = message.from_user.id

    clans = get_user_clans(user_id)

    if not clans:
        await message.answer("❌ Вы не состоите ни в одном клане")
        return

    text = "🏰 Твои кланы:\n\n"

    for clan_id, public_id, name, role, dkp in clans:
        role_emoji = "👑" if role == "leader" else "👤"
        text += f"{role_emoji} {name} (ID: {public_id})\n"

    text += "\nВведите ID клана, из которого хотите выйти:"

    await message.answer(text)
    await state.set_state(LeaveClan.waiting_for_clan_id)


# ВВОД ID
@router.message(LeaveClan.waiting_for_clan_id)
async def process_clan_id(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введи числовой ID")
        return

    public_id = int(message.text)
    user_id = message.from_user.id

    # 🔍 проверяем клан
    clan = get_clan_by_public_id(public_id)

    if not clan:
        await message.answer("❌ Клан не найден")
        return

    clan_id, public_id, clan_name = clan

    # 🔍 проверяем, состоит ли пользователь в этом клане
    user_clans = get_user_clans(user_id)
    valid_ids = [c[1] for c in user_clans]

    if public_id not in valid_ids:
        await message.answer("❌ Вы не состоите в этом клане")
        return

    # 🔍 проверяем роль
    role = next((r for clan_id, pid, name, r, d in user_clans if pid == public_id), None)

    if role == "leader":
        await message.answer("❌ Лидер не может покинуть клан. Удалите клан или передайте лидерство.")
        return

    await state.update_data(clan_id=clan_id, clan_name=clan_name)

    await message.answer(
        f"⚠️ Вы точно хотите покинуть клан '{clan_name}'?\n\nНапишите LEAVE_CLAN для подтверждения"
    )

    await state.set_state(LeaveClan.waiting_for_confirmation)


# ✅ ПОДТВЕРЖДЕНИЕ
@router.message(LeaveClan.waiting_for_confirmation)
async def confirm_leave(message: Message, state: FSMContext):
    if message.text != "LEAVE_CLAN":
        await message.answer("❌ Выход отменён")
        await state.clear()
        return

    data = await state.get_data()

    clan_id = data["clan_id"]
    clan_name = data["clan_name"]

    leave_clan(clan_id, message.from_user.id)

    await message.answer(f"🚪 Вы покинули клан '{clan_name}'")
    await state.clear()