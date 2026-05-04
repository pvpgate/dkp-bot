from aiogram import Router, types
from aiogram.filters import Command

from keyboards.inline.menu_buttons import main_menu, clan_menu, event_menu, clan_manage_menu

router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "Добро пожаловать! Выберите действие:",
        reply_markup=main_menu()
    )


# 🏰 Меню кланов
@router.callback_query(lambda c: c.data == "clan_menu")
async def open_clan_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🏰 Меню кланов:",
        reply_markup=clan_menu()
    )
    await callback.answer()

@router.callback_query(lambda c: c.data == "clan_manage")
async def open_clan_manage(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "⚙️ Управление кланами:",
        reply_markup=clan_manage_menu()
    )
    await callback.answer()

# 🎯 Меню ивентов
@router.callback_query(lambda c: c.data == "event_menu")
async def open_event_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🎯 Меню ивентов:",
        reply_markup=event_menu()
    )
    await callback.answer()


# 🔙 Назад
@router.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=main_menu()
    )
    await callback.answer()
    

@router.callback_query(lambda c: c.data == "back_to_clans")
async def back_to_clans(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🏰 Меню кланов:",
        reply_markup=clan_menu()
    )
    await callback.answer()