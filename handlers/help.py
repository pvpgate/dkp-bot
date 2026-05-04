from aiogram import Router, types
from aiogram.filters import Command

router = Router()


HELP_TEXT = """
📖 Помощь по боту

Основные команды:

/start — открыть главное меню
/help — показать это сообщение

🏰 Кланы:
/create_clan — создать клан
/my_clans — посмотреть свои кланы и заявки
/delete_clan - удалить клан (будут далены все участники и накопленные ими dkp)

📩 Заявки:
— отправить заявку через кнопку "Присоединиться"
— статус заявки отображается в "Мои кланы"

🎯 Возможности:
— участие в ивентах
— система DKP
— управление кланом (для лидеров)

Если что-то не работает — пиши разработчику 😄
"""


# команда /help
@router.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(HELP_TEXT)


# кнопка "Помощь"
@router.callback_query(lambda c: c.data == "help")
async def help_callback(callback: types.CallbackQuery):
    await callback.message.answer(HELP_TEXT)
    await callback.answer()