from aiogram import Router, types
from db import cursor, conn
from aiogram.filters import Command
from aiogram.types import Message
from database.db_queries import get_user_clans, get_user_clan_requests

router = Router()


async def build_clans_text(user_id: int):
    clans = get_user_clans(user_id)
    requests = get_user_clan_requests(user_id)

    if not clans:
        return "❌ Вы не состоите ни в одном клане"

    text = "🏰 Ваши кланы:\n\n"

    for clan_id, public_id, name, role, dkp in clans:
        role_emoji = "👑" if role == "leader" else "👤"
        text += f"{role_emoji} {name}\n   ID: {public_id}\n   Роль: {role}\n   DKP: {dkp}\n\n"

    text += "📩 Ваши заявки:\n"

    if requests:
        for clan_name, public_id, status in requests:
            if status != 'accepted':
                status_emoji = "⏳" if status == "pending" else "❌" if status == "rejected" else "✅"
                text += f"- {clan_name} | {status_emoji} {status}\n"
            else:
                text += "- нет заявок\n"
    else:
        text += "- нет заявок\n"

    return text

# вызов функции по кнопке
@router.callback_query(lambda c: c.data == "my_clans")
async def show_my_clans(callback: types.CallbackQuery):
    text = await build_clans_text(callback.from_user.id)
    await callback.message.answer(text)
    await callback.answer()

# вызов функции командой в чате
@router.message(Command("my_clans"))
async def show_my_clans_command(message: Message):
    text = await build_clans_text(message.from_user.id)
    await message.answer(text)