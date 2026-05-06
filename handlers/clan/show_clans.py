from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message

from database.queries.clans import get_user_clans
from database.queries.requests import get_user_clan_requests

router = Router()


async def build_clans_text(user_id: int):
    clans = await get_user_clans(user_id)
    requests = await get_user_clan_requests(user_id)

    if not clans:
        return "❌ Вы не состоите ни в одном клане"

    text = "🏰 Ваши кланы:\n\n"

    for clan in clans:
        role_emoji = "👑" if clan["role"] == "leader" else "👤"

        text += (
            f"{role_emoji} {clan['name']}\n"
            f"   ID: {clan['public_id']}\n"
            f"   Роль: {clan['role']}\n"
            f"   DKP: {clan['dkp']}\n\n"
        )

    text += "📩 Ваши заявки:\n"

    # фильтруем только не-accepted заявки
    filtered_requests = [
        r for r in requests if r["status"] != "accepted"
    ]

    if filtered_requests:
        for req in filtered_requests:
            status_emoji = (
                "⏳" if req["status"] == "pending"
                else "❌" if req["status"] == "rejected"
                else "✅"
            )

            text += f"- {req['name']} | {status_emoji} {req['status']}\n"
    else:
        text += "- нет заявок\n"

    return text


# 📋 кнопка
@router.callback_query(lambda c: c.data == "my_clans")
async def show_my_clans(callback: types.CallbackQuery):
    text = await build_clans_text(callback.from_user.id)
    await callback.message.answer(text)
    await callback.answer()


# 📋 команда
@router.message(Command("my_clans"))
async def show_my_clans_command(message: Message):
    text = await build_clans_text(message.from_user.id)
    await message.answer(text)