from aiogram.fsm.state import StatesGroup, State
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database.db_queries import get_user_clans, delete_clan_by_public_id

router = Router()

class DeleteClan(StatesGroup):
    waiting_for_clan_id = State()
    waiting_for_confirmation = State()


# 🚀 ОБЩАЯ ЛОГИКА СТАРТА
async def start_delete_flow(event, state: FSMContext):
    user_id = event.from_user.id

    clans = get_user_clans(user_id)
    allowed = [c for c in clans if c[3] in ("leader")]

    if not allowed:
        await send_answer(event, "❌ У вас нет кланов, где вы лидер")
        return

    text = "🏰 Ваши кланы (вы лидер):\n\n"

    for clan_id, public_id, name, role, dkp in allowed:
        text += f"ID: {public_id} — {name}\n"

    text += "\nВведите ID клана, который хочешь удалить:"

    await send_answer(event, text)
    await state.set_state(DeleteClan.waiting_for_clan_id)

@router.message(Command("delete_clan"))
async def start_delete_clan(message: types.Message, state: FSMContext):
    await start_delete_flow(message, state)


@router.callback_query(lambda c: c.data == "delete_clan")
async def start_delete_clan_btn(callback: types.CallbackQuery, state: FSMContext):
    await start_delete_flow(callback, state)
    

async def send_answer(event, text):
    if isinstance(event, types.CallbackQuery):
        await event.message.answer(text)
        await event.answer()
    else:
        await event.answer(text)

# 2. Ввод ID
@router.message(DeleteClan.waiting_for_clan_id)
async def process_clan_id(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введи числовой ID клана")
        return

    public_id = int(message.text)
    user_id = message.from_user.id

    clans = get_user_clans(user_id)
    valid_ids = [c[1] for c in clans]

    if public_id not in valid_ids:
        await message.answer("❌ У тебя нет прав на этот клан")
        return

    clan_name = next((name for cid, pid, name, r, d in clans if pid == public_id), None)

    await state.update_data(public_id=public_id)

    await message.answer(
        f"⚠️ Вы точно хотите удалить клан {clan_name}? Все члены клана и накопленные ДКП будут удалены. Это действие будет невозможно отменить\n\nНапиши DELETE для подтверждения"
    )

    await state.set_state(DeleteClan.waiting_for_confirmation)


# 3. Подтверждение
@router.message(DeleteClan.waiting_for_confirmation)
async def confirm_delete(message: types.Message, state: FSMContext):
    if message.text != "DELETE":
        await message.answer("❌ Удаление отменено")
        await state.clear()
        return

    data = await state.get_data()
    public_id = data["public_id"]

    delete_clan_by_public_id(public_id)

    await message.answer("💥 Клан успешно удалён")
    await state.clear()