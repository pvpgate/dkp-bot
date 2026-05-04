from aiogram import Router, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards.inline.menu_buttons import (
    clan_members_actions,
    clan_select_keyboard
)

from database.db_queries import (
    get_user_clans,
    get_clan_members
)

router = Router()


# 🚀 кнопка
@router.callback_query(lambda c: c.data == "clan_members")
async def start_members(callback: CallbackQuery, state: FSMContext):
    await start_flow(callback)


# 🚀 команда
@router.message(Command("clan_members"))
async def start_members_cmd(message: Message, state: FSMContext):
    await start_flow(message)


# 🔧 старт — показываем кланы КНОПКАМИ
async def start_flow(event):
    user_id = event.from_user.id

    clans = get_user_clans(user_id)
    allowed = [c for c in clans if c[3] in ("leader", "officer")]

    if not allowed:
        await send_answer(event, "❌ У вас нет доступа к этому разделу")
        return

    text = "🏰 Выберите клан:"

    if isinstance(event, CallbackQuery):
        await event.message.answer(
            text,
            reply_markup=clan_select_keyboard(allowed)
        )
        await event.answer()
    else:
        await event.answer(
            text,
            reply_markup=clan_select_keyboard(allowed)
        )


# 🧠 выбор клана
@router.callback_query(lambda c: c.data.startswith("select_clan:"))
async def process_clan(callback: CallbackQuery, state: FSMContext):
    clan_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    clans = get_user_clans(user_id)
    allowed = [c for c in clans if c[3] in ("leader", "officer")]
    valid_ids = [c[1] for c in allowed]

    if clan_id not in valid_ids:
        await callback.answer("❌ Нет доступа к этому клану", show_alert=True)
        return

    members = get_clan_members(clan_id)

    if not members:
        await callback.message.answer("❌ В клане нет участников")
        await callback.answer()
        return

    text = "👥 Участники и ДКП:\n\n"

    role_map = {
        "leader": "👑 Лидер",
        "officer": "⭐ Офицер",
        "member": "👤 Участник"
    }

    for user_id_m, username, role, dkp in members:
        role_text = role_map.get(role, role)
        text += f"{role_text} {username}\n   ID: {user_id_m} | DKP: {dkp}\n\n"

    await callback.message.answer(
        text,
        reply_markup=clan_members_actions(clan_id)
    )

    await callback.answer()


# 🔧 универсальный ответ
async def send_answer(event, text):
    if isinstance(event, CallbackQuery):
        await event.message.answer(text)
        await event.answer()
    else:
        await event.answer(text)