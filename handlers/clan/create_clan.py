from aiogram import Router, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from db_queries import create_clan_db

router = Router()


class CreateClan(StatesGroup):
    waiting_for_name = State()


def validate_clan_name(name: str):
    name = name.strip()

    if len(name) < 3:
        return False, "CLAN_NAME_TOO_SHORT"

    if len(name) > 16:
        return False, "CLAN_NAME_TOO_LONG"

    if not name.isalnum():
        return False, "INVALID_CHARACTERS"

    return True, name


@router.message(Command("create_clan"))
async def start_create_clan_command(message: Message, state: FSMContext):
    await message.answer("Введите название клана:")
    await state.set_state(CreateClan.waiting_for_name)


@router.callback_query(lambda c: c.data == "create_clan")
async def start_create_clan(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название клана:")
    await state.set_state(CreateClan.waiting_for_name)


@router.message(CreateClan.waiting_for_name)
async def process_clan_name(message: types.Message, state: FSMContext):

    is_valid, result = validate_clan_name(message.text)

    if not is_valid:
        if result == "CLAN_NAME_TOO_SHORT":
            await message.answer("❌ Название слишком короткое (мин. 3 символа)")
        elif result == "CLAN_NAME_TOO_LONG":
            await message.answer("❌ Название слишком длинное (макс. 16 символов)")
        elif result == "INVALID_CHARACTERS":
            await message.answer("❌ Название может содержать только буквы и цифры")
        return

    name = result

    db_result = await create_clan_db(
        name=name,
        owner_id=message.from_user.id,
        owner_name=message.from_user.username
    )

    if not db_result["ok"]:
        if db_result["error"] == "CLAN_ALREADY_EXISTS":
            await message.answer("❌ Клан с таким названием уже существует")
        return

    await message.answer(
        f"🎉 Клан '{db_result['name']}' создан!\nID: {db_result['public_id']}"
    )

    await state.clear()