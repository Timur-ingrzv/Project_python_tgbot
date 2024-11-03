import asyncio
import config
from aiogram import Bot, Dispatcher
from aiogram.filters.command import Command, Message

from utils.filters import IsStudentFilter, IsTeacherFilter, UserStatus
from utils.middleware import StatusMiddleware, User_status
from handlers import handlers_for_students, handlers_for_teacher
from keyboards.keyboards_for_unauthorized_user import get_start_keyboard

# Объект бота
bot = Bot(token=config.TOKEN)
# Диспетчер
dp = Dispatcher()

# Запуск процесса поллинга новых апдейтов
async def main():
    dp.update.middleware(StatusMiddleware())
    dp.include_routers(handlers_for_students.router, handlers_for_teacher.router)

    handlers_for_students.router.callback_query.filter(IsStudentFilter())

    handlers_for_teacher.router.callback_query.filter(IsTeacherFilter())

    await dp.start_polling(bot)

@dp.message(Command("start"))
async def cmd_start(message: Message):
    User_status[message.from_user.id] = UserStatus.UNAUTHORIZED_USER
    await message.answer(f"Привет!\nЯ помощник для организации учебы",
                         reply_markup=get_start_keyboard())

if __name__ == "__main__":
    asyncio.run(main())
