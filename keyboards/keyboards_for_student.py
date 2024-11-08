from aiogram import types


def get_interface_for_student():
    buttons = [
        [
            types.InlineKeyboardButton(
                text="Посмотреть запланированные уроки",
                callback_data="show schedule",
            )
        ],
        [
            types.InlineKeyboardButton(
                text="Посмотреть ДЗ", callback_data="show hw"
            )
        ],
        [
            types.InlineKeyboardButton(
                text="Отправить выполненное ДЗ", callback_data="send hw"
            )
        ],
        [
            types.InlineKeyboardButton(
                text="Выйти из профиля", callback_data="exit profile"
            )
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
