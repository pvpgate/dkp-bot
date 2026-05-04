from aiogram import Router, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from database.db_queries import (
    get_user_clans,
    get_clan_members,
    remove_member_from_clan
)

router = Router()


# 🔹 FSM (только нужные шаги)
class DismissMember(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_confirmation = State()


# 🚀 СТАРТ (кнопка с public_id)
@router.callback_query(lambda c: c.data.startswith("dismiss_member:"))
async def start_dismiss(callback: CallbackQuery, state: FSMContext):
    public_id = int(callback.data.split(":")[1])

    # сохраняем клан
    await state.update_data(clan_id=public_id)

    await callback.message.answer("Введите ID игрока для исключения:")

    await state.set_state(DismissMember.waiting_for_user_id)
    await callback.answer()


# 🧠 ВВОД УЧАСТНИКА
@router.message(DismissMember.waiting_for_user_id)
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

    if target_user_id == message.from_user.id:
        await message.answer("❌ Нельзя исключить себя")
        return

    target_member = next((m for m in members if m[0] == target_user_id), None)

    if not target_member:
        await message.answer("❌ Игрок не найден")
        return

    target_role = target_member[2]

    members_dict = {m[0]: m[2] for m in members}
    my_role = members_dict.get(message.from_user.id)

    # ❌ пользователь вообще не состоит в клане
    if not my_role:
        await message.answer("❌ У вас нет прав на управление этим кланом")
        await state.clear()
        return

    # ❌ офицер ограничения
    if my_role == "officer" and target_role in ("officer", "leader"):
        await message.answer("❌ Офицер не может исключать офицера или лидера")
        return

    # ❌ лидер тоже нельзя через баги обойти
    if target_role == "leader":
        await message.answer("❌ Нельзя исключить лидера")
        return

    await state.update_data(target_user_id=target_user_id)

    await message.answer(
        f"⚠️ Исключить игрока {target_member[1]}?\n\nНапишите DISMISS для подтверждения"
    )

    await state.set_state(DismissMember.waiting_for_confirmation)


# ⚙️ ПОДТВЕРЖДЕНИЕ
@router.message(DismissMember.waiting_for_confirmation)
async def confirm(message: Message, state: FSMContext):
    if message.text != "DISMISS":
        await message.answer("❌ Отменено")
        await state.clear()
        return

    data = await state.get_data()
    clan_id = data["clan_id"]
    target_user_id = data["target_user_id"]

    remove_member_from_clan(clan_id, target_user_id)

    await message.answer("🚪 Игрок исключён из клана")
    await state.clear()