import asyncio

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import config
from aiogram import Bot, Dispatcher
from aiogram.filters.command import Command, Message

from handlers import (
    handlers_for_students,
    handlers_for_teacher,
    handlers_for_unauthorized_user,
)
from keyboards.keyboards_for_unauthorized_user import get_start_keyboard

# Объект бота
bot = Bot(
    token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
# Диспетчер
dp = Dispatcher()


# Запуск процесса поллинга новых апдейтов
async def main():
    dp.include_routers(
        handlers_for_students.router,
        handlers_for_teacher.router,
        handlers_for_unauthorized_user.router,
    )

    await dp.start_polling(bot)


@dp.message(Command("start"))
async def cmd_start(message: Message, bot: Bot):
    await bot.send_message(
        chat_id=message.chat.id,
        text="Привет!\nЯ помощник для организации учебы",
        reply_markup=get_start_keyboard(),
    )


if __name__ == "__main__":
    asyncio.run(main())
