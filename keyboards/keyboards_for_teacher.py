from aiogram import types


def get_interface_for_teacher():
    buttons = [
        [
            types.InlineKeyboardButton(
                text="Добавить пользователя", callback_data="add user"
            ),
            types.InlineKeyboardButton(
                text="Удалить пользователя", callback_data="remove user"
            ),
        ],
        [
            types.InlineKeyboardButton(
                text="Добавить занятие", callback_data="add lesson"
            ),
            types.InlineKeyboardButton(
                text="Удалить занятие", callback_data="remove lesson"
            ),
        ],
        [
            types.InlineKeyboardButton(
                text="Добавить ДЗ", callback_data="add hw"
            ),
            types.InlineKeyboardButton(
                text="Удалить ДЗ", callback_data="remove hw"
            ),
        ],
        [
            types.InlineKeyboardButton(
                text="Посмотреть уроки",
                callback_data="show lesson for teacher",
            ),
            types.InlineKeyboardButton(
                text="Посмотреть дз ученика",
                callback_data="show hw for teacher",
            ),
        ],
        [
            types.InlineKeyboardButton(
                text="Статистика", callback_data="get statistic interface"
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
