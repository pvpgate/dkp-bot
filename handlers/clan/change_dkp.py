from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from database.db_queries import (
    get_clan_members,
    update_member_dkp,
    get_clan_by_public_id
)

router = Router()


# 🔹 FSM
class ChangeDKP(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_amount = State()


# 🚀 СТАРТ (кнопка с public_id)
@router.callback_query(lambda c: c.data.startswith("change_dkp:"))
async def start_change_dkp(callback: CallbackQuery, state: FSMContext):
    public_id = int(callback.data.split(":")[1])

    # сохраняем клан
    await state.update_data(clan_id=public_id)

    await callback.message.answer("Введите ID игрока для изменения ДКП:")
    await state.set_state(ChangeDKP.waiting_for_user_id)

    await callback.answer()


# 🧠 ВВОД ИГРОКА
@router.message(ChangeDKP.waiting_for_user_id)
async def process_user(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введи числовой ID")
        return

    target_user_id = int(message.text)

    data = await state.get_data()
    public_clan_id = data["clan_id"]

    members = get_clan_members(public_clan_id)
    member_ids = [m[0] for m in members]

    if target_user_id not in member_ids:
        await message.answer("❌ Игрок не найден в этом клане")
        return

    # получаем игрока
    target_member = next((m for m in members if m[0] == target_user_id), None)

    if not target_member:
        await message.answer("❌ Игрок не найден")
        return

    username = target_member[1]
    current_dkp = target_member[3]

    await state.update_data(target_user_id=target_user_id)

    await message.answer(
        f"👤 Игрок: {username}\n"
        f"💰 Текущий ДКП: {current_dkp}\n\n"
        "Введите изменение ДКП:\n\n"
        "Примеры:\n"
        "+100 — добавить\n"
        "-50 — отнять"
    )

    await state.set_state(ChangeDKP.waiting_for_amount)


# 🧠 ВВОД ДКП
@router.message(ChangeDKP.waiting_for_amount)
async def process_amount(message: Message, state: FSMContext):
    value = message.text.strip()

    # проверка формата
    if not (value.startswith("+") or value.startswith("-")):
        await message.answer("❌ Используй формат +100 или -50")
        return

    if not value[1:].isdigit():
        await message.answer("❌ После знака должно быть число")
        return

    dkp_change = int(value)

    data = await state.get_data()
    public_clan_id = data["clan_id"]
    target_user_id = data["target_user_id"]

    # получаем реальный clan_id
    clan_id, _, _ = get_clan_by_public_id(public_clan_id)

    members = get_clan_members(public_clan_id)
    target_member = next((m for m in members if m[0] == target_user_id), None)

    if not target_member:
        await message.answer("❌ Игрок не найден")
        await state.clear()
        return

    current_dkp = target_member[3]
    new_dkp = current_dkp + dkp_change

    # защита от минуса
    if new_dkp < 0:
        await message.answer("❌ ДКП не может быть меньше 0")
        return

    update_member_dkp(clan_id, target_user_id, new_dkp)

    await message.answer(
        f"✅ ДКП обновлено\n"
        f"Было: {current_dkp}\n"
        f"Стало: {new_dkp}"
    )

    await state.clear()