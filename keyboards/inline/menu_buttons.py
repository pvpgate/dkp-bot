from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# 🔹 Главное меню
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏰 Меню кланов", callback_data="clan_menu")],
        [InlineKeyboardButton(text="🎯 Меню ивентов", callback_data="event_menu")],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="help")]
    ])


def clan_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Мои кланы", callback_data="my_clans")],
        [InlineKeyboardButton(text="🔗 Присоединиться", callback_data="join_clan")],
        [InlineKeyboardButton(text="🚪 Покинуть клан", callback_data="leave_clan")],
        [InlineKeyboardButton(text="⚙️ Управление кланами", callback_data="clan_manage")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])

def clan_manage_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏰 Создать клан", callback_data="create_clan")],
        [InlineKeyboardButton(text="📩 Заявки", callback_data="view_requests")],
        [InlineKeyboardButton(text="👥 Участники и ДКП", callback_data="clan_members")],
        [InlineKeyboardButton(text="💥 Удалить клан", callback_data="delete_clan")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_clans")]
    ])

# 🔹 Меню ивентов
def event_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Создать ивент", callback_data="create_event")],
        [InlineKeyboardButton(text="✅ Присоединиться", callback_data="join_event")],
        [InlineKeyboardButton(text="🚪 Покинуть ивент", callback_data="leave_event")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])

def request_action_keyboard(request_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Принять",callback_data=f"accept_request:{request_id}"),
         InlineKeyboardButton(text="❌ Отклонить",callback_data=f"reject_request:{request_id}")]
    ])


def clan_members_actions(public_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔼 Назначить роль",
                callback_data=f"assign_role:{public_id}"
            ),
            InlineKeyboardButton(
                text="❌ Исключить",
                callback_data=f"dismiss_member:{public_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="💰 Изменить ДКП",
                callback_data=f"change_dkp:{public_id}"
            )
        ]
    ])

def clan_select_keyboard(clans):
    keyboard = []

    for clan_id, public_id, name, role, dkp in clans:
        keyboard.append([
            InlineKeyboardButton(
                text=f"🏰 {name} ({role})",
                callback_data=f"select_clan:{public_id}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Открыть ДКП",
            web_app=WebAppInfo(url="https://your-domain.com")
        )]
    ])