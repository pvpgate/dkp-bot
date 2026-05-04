from aiogram import Router, types
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from database.db_queries import (
    get_user_clans,
    get_pending_requests_for_clans,
    get_request_by_id,
    accept_request,
    reject_request
)

router = Router()


# 🔹 КНОПКИ
def request_action_keyboard(request_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Принять",
                callback_data=f"accept_request:{request_id}"
            ),
            InlineKeyboardButton(
                text="❌ Отклонить",
                callback_data=f"reject_request:{request_id}"
            )
        ]
    ])


# 🚀 СТАРТ (кнопка)
@router.callback_query(lambda c: c.data == "view_requests")
async def start_requests(callback: CallbackQuery):
    await show_requests(callback)


# 🚀 СТАРТ (команда)
@router.message(Command("requests"))
async def start_requests_cmd(message: Message):
    await show_requests(message)


# 🔧 ОБЩАЯ ЛОГИКА
async def show_requests(event):
    user_id = event.from_user.id

    clans = get_user_clans(user_id)

    # только leader/officer
    allowed_clans = [c for c in clans if c[3] in ("leader", "officer")]

    if not allowed_clans:
        await send_answer(event, "❌ У вас нет прав на просмотр заявок")
        return

    clan_ids = [c[0] for c in allowed_clans]

    requests = get_pending_requests_for_clans(clan_ids)

    if not requests:
        await send_answer(event, "📭 Нет заявок")
        return

    # 🔥 теперь каждая заявка отдельным сообщением с кнопками
    for req_id, user_id_req, username_req, clan_name in requests:
        text = f"📩 Заявка #{req_id}\n👤 {username_req} → 🏰 {clan_name}"

        await send_answer(
            event,
            text,
            reply_markup=request_action_keyboard(req_id)
        )


# =========================
# 🔹 ПРИНЯТЬ
# =========================
@router.callback_query(lambda c: c.data.startswith("accept_request:"))
async def handle_accept(callback: CallbackQuery):
    request_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    request = get_request_by_id(request_id)

    if not request:
        await callback.answer("❌ Заявка не найдена", show_alert=True)
        return

    req_id, target_user_id, target_username, clan_id, status = request

    if status != "pending":
        await callback.answer("❌ Уже обработано", show_alert=True)
        return

    # проверка прав
    clans = get_user_clans(user_id)
    allowed_clans = [c[0] for c in clans if c[3] in ("leader", "officer")]

    if clan_id not in allowed_clans:
        await callback.answer("❌ Нет прав", show_alert=True)
        return

    accept_request(request_id, target_user_id, target_username, clan_id)

    await callback.message.edit_text("✅ Игрок принят в клан")
    await callback.answer()


# =========================
# 🔹 ОТКЛОНИТЬ
# =========================
@router.callback_query(lambda c: c.data.startswith("reject_request:"))
async def handle_reject(callback: CallbackQuery):
    request_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    request = get_request_by_id(request_id)

    if not request:
        await callback.answer("❌ Заявка не найдена", show_alert=True)
        return

    req_id, target_user_id, target_username, clan_id, status = request

    if status != "pending":
        await callback.answer("❌ Уже обработано", show_alert=True)
        return

    # проверка прав
    clans = get_user_clans(user_id)
    allowed_clans = [c[0] for c in clans if c[3] in ("leader", "officer")]

    if clan_id not in allowed_clans:
        await callback.answer("❌ Нет прав", show_alert=True)
        return

    reject_request(request_id)

    await callback.message.edit_text("❌ Заявка отклонена")
    await callback.answer()


# 🔧 универсальный ответ
async def send_answer(event, text, reply_markup=None):
    if isinstance(event, CallbackQuery):
        await event.message.answer(text, reply_markup=reply_markup)
        await event.answer()
    else:
        await event.answer(text, reply_markup=reply_markup)