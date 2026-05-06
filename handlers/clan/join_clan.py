from aiogram import Router, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from database.queries.requests import create_clan_request

router = Router()


# 🔹 FSM
class JoinClan(StatesGroup):
    waiting_for_clan_id = State()


# 🔹 старт через команду
@router.message(Command("join_clan"))
async def join_clan_command(message: Message, state: FSMContext):
    await message.answer("🏰 Введите ID клана:")
    await state.set_state(JoinClan.waiting_for_clan_id)


# 🔹 старт через кнопку
@router.callback_query(lambda c: c.data == "join_clan")
async def join_clan_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🏰 Введите ID клана:")
    await state.set_state(JoinClan.waiting_for_clan_id)
    await callback.answer()


# 🔹 обработка ID
@router.message(JoinClan.waiting_for_clan_id)
async def process_join_clan(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username or "unknown"

    # проверка числа
    if not message.text.isdigit():
        await message.answer("❌ ID клана должен быть числом")
        return

    public_id = int(message.text)

    result = await create_clan_request(
        user_id=user_id,
        username=username,
        public_id=public_id
    )

    if not result["ok"]:
        if result["error"] == "CLAN_NOT_FOUND":
            await message.answer("❌ Клан не найден")
        elif result["error"] == "ALREADY_IN_THIS_CLAN":
            await message.answer("❌ Вы уже состоите в этом клане")
        elif result["error"] == "REQUEST_ALREADY_EXISTS":
            await message.answer("⏳ Вы уже отправили заявку в этот клан")
        return

    await message.answer("✅ Заявка отправлена!")

    await state.clear()