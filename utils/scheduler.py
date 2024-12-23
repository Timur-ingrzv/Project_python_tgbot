import asyncio
import datetime
import logging

from database.methods import db


async def scheduler_notification_lesson(user_id: int, chat_id: int):
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


async def scheduler_set_deadline(
    wait_time: datetime.timedelta, student_name: str, reference: str
):
    await asyncio.sleep(wait_time.seconds)
    student = await db.get_user_id(student_name)
    if student:
        await db.set_hw_deadline(student["user_id"], reference)
        logging.info(
            f"статус дз для {student_name} изменен по истечению дедлайна"
        )
