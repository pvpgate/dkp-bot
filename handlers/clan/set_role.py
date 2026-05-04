from aiogram import Router, types
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from database.db_queries import (
    get_user_clans,
    get_clan_members,
    update_member_role,
    get_clan_by_public_id
)

router = Router()


# 🔹 FSM
class SetRole(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_role = State()


# 🚀 старт (кнопка с public_id)
@router.callback_query(lambda c: c.data.startswith("assign_role:"))
async def start_set_role(callback: CallbackQuery, state: FSMContext):
    public_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    clans = get_user_clans(user_id)

    # ищем клан и роль пользователя
    clan_data = next((c for c in clans if c[1] == public_id), None)

    if not clan_data:
        await callback.message.answer("❌ У вас нет доступа к этому клану")
        await callback.answer()
        return

    role = clan_data[3]

    # ❌ только лидер может менять роли
    if role != "leader":
        await callback.message.answer("❌ Только лидер может назначать роли")
        await callback.answer()
        return

    # сохраняем клан
    await state.update_data(clan_id=public_id)

    await callback.message.answer("Введите ID игрока для изменения роли:")
    await state.set_state(SetRole.waiting_for_user_id)

    await callback.answer()


# 🚀 команда (оставим как fallback — можно убрать если не нужно)
@router.message(Command("set_role"))
async def start_set_role_cmd(message: Message, state: FSMContext):
    await message.answer("Используйте кнопку 'Назначить роль' в меню клана.")
    await state.clear()


# 🧠 ввод игрока
@router.message(SetRole.waiting_for_user_id)
async def process_user(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введи числовой ID")
        return

    target_user_id = int(message.text)
    data = await state.get_data()
    clan_id = data["clan_id"]

    members = get_clan_members(clan_id)
    member_ids = [m[0] for m in members]

    if target_user_id not in member_ids:
        await message.answer("❌ Игрок не найден в этом клане")
        return

    # ❌ нельзя менять роль себе
    if target_user_id == message.from_user.id:
        await message.answer("❌ Нельзя менять роль себе")
        return

    target_member = next((m for m in members if m[0] == target_user_id), None)

    if not target_member:
        await message.answer("❌ Игрок не найден")
        return

    target_role = target_member[2]

    # ❌ нельзя менять роль лидера
    if target_role == "leader":
        await message.answer("❌ Нельзя менять роль лидера")
        return

    await state.update_data(target_user_id=target_user_id)

    # 🔥 кнопки выбора роли
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Офицер", callback_data="role_officer")],
        [InlineKeyboardButton(text="👤 Участник", callback_data="role_member")]
    ])

    await message.answer("Выбери новую роль:", reply_markup=keyboard)
    await state.set_state(SetRole.waiting_for_role)


# ⚙️ выбор роли
@router.callback_query(SetRole.waiting_for_role)
async def process_role(callback: CallbackQuery, state: FSMContext):
    role_map = {
        "role_officer": "officer",
        "role_member": "member"
    }

    if callback.data not in role_map:
        await callback.answer("❌ Ошибка")
        return

    new_role = role_map[callback.data]

    data = await state.get_data()
    public_clan_id = data["clan_id"]
    clan_id, public_id, name = get_clan_by_public_id(public_clan_id)
    target_user_id = data["target_user_id"]

    update_member_role(clan_id, target_user_id, new_role)

    await callback.message.answer("✅ Роль успешно обновлена")
    await callback.answer()
    await state.clear()