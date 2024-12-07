import asyncio
import logging

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import config
from aiogram import Bot, Dispatcher
from aiogram.filters.command import Command, Message

from handlers import (
    handlers_for_students,
    handlers_for_teacher,
    handlers_for_unauthorized_user,
    handlers_statistic_for_teacher,
)
from keyboards.keyboards_for_unauthorized_user import get_start_keyboard

# Объект бота
bot = Bot(
    token=config.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
# Диспетчер
dp = Dispatcher()

notifications = {}


# Запуск процесса поллинга новых апдейтов
async def main():
    dp.include_routers(
        handlers_for_students.router,
        handlers_for_teacher.router,
        handlers_for_unauthorized_user.router,
        handlers_statistic_for_teacher.router,
    )
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


@dp.message(Command("start"))
async def cmd_start(message: Message, bot: Bot, prev_user_id=None):
    # останавливаем уведомления
    if prev_user_id:
        try:
            notifications[prev_user_id].cancel()
            del notifications[prev_user_id]
        except Exception as e:
            logging.error(e)

    await bot.send_message(
        chat_id=message.chat.id,
        text="Привет!\nЯ помощник для организации учебы",
        reply_markup=get_start_keyboard(),
    )


if __name__ == "__main__":
    asyncio.run(main())
