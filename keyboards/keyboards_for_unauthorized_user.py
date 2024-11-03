from aiogram import types


def get_start_keyboard():
    buttons = [
        [types.InlineKeyboardButton(text="Авторизироваться", callback_data="authorization")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard