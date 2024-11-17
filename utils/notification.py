import asyncio

from pyexpat.errors import messages

from database.methods import db


async def scheduler(user_id: int, chat_id: int):
    from bot import bot

    try:
        while True:
            res = await db.find_lesson(user_id)
            if res:
                for lesson in res:
                    message = (
                        f"Напоминание об уроке:\n"
                        f"<b>Дата:</b> {lesson['date']}\n"
                        f"<b>Тема:</b> {lesson['topic']}"
                    )
                    await bot.send_message(chat_id, message)

            # Проверка каждые 60 минут
            await asyncio.sleep(3600)
    except Exception:
        return
