import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging
from webbrowser import Opera

import asyncpg
from pypika import Table, Query, Order
from config import DATABASE_CONFIG


class MethodsForStudent:
    def __init__(self, config):
        self.db_config = config
        self.users = Table("users")
        self.schedule = Table("schedule")
        self.hw = Table("homework")

    async def find_user(self, login: str, password: str) -> Dict:
        connection = await asyncpg.connect(**self.db_config)
        try:
            # Создание запроса с использованием Pypika
            query = (
                Query.from_(self.users)
                .select(self.users.user_id, self.users.name, self.users.status)
                .where(
                    (self.users.login == login)
                    & (self.users.password == password)
                )
            )

            # Получение одной строки
            res = await connection.fetchrow(str(query))

            # Возврат результата
            if not res:
                return {"status": "User not found"}
            else:
                return {
                    "user_id": res["user_id"],
                    "name": res["name"],
                    "status": res["status"],
                }
        finally:
            # Закрытие соединения
            await connection.close()

    async def get_future_events(self, user_id: int) -> tuple[Dict]:
        now = datetime.now()
        connection = await asyncpg.connect(**self.db_config)
        try:
            query = (
                Query.from_(self.schedule)
                .join(self.users)
                .on(self.users.user_id == self.schedule.teacher_id)
                .select(
                    self.users.name, self.schedule.date, self.schedule.topic
                )
                .where(self.schedule.date > now)
                .where(self.schedule.student_id == user_id)
                .orderby(self.schedule.date, order=Order.asc)
                .limit(5)
            )
            res = await connection.fetch(str(query))
            return res
        finally:
            await connection.close()

    async def get_homework(self, user_id: int) -> tuple[Dict]:
        connection = await asyncpg.connect(**self.db_config)
        try:
            query = (
                Query.from_(self.hw)
                .select(
                    self.hw.topic,
                    self.hw.reference,
                    self.hw.deadline,
                    self.hw.status,
                )
                .where(self.hw.status != "Deadline")
                .where(self.hw.student_id == user_id)
            )
            res = await connection.fetch(str(query))
            return res
        finally:
            await connection.close()

    async def get_name(self, user_id: int) -> str:
        connection = await asyncpg.connect(**self.db_config)
        try:
            query = (
                Query.from_(self.users)
                .select(self.users.name)
                .where(self.users.user_id == user_id)
            )
            res = await connection.fetch(str(query))
            return res[0]["name"]

        except Exception as e:
            logging.info(e)

        finally:
            await connection.close()

    async def check_ref_hw(self, user_id: int, ref: str) -> bool:
        connection = await asyncpg.connect(**self.db_config)
        try:
            query = (
                Query.from_(self.hw)
                .select(self.hw.hw_id)
                .where(self.hw.reference == ref)
                .where(self.hw.student_id == user_id)
                .where(self.hw.status != "deadline")
            )
            res = await connection.fetch(str(query))
            return bool(res)
        finally:
            await connection.close()

    async def set_status_done(self, student_id: int, hw_reference: str):
        connection = await asyncpg.connect(**self.db_config)
        try:
            query = (
                Query.update(self.hw)
                .set(self.hw.status, "done")
                .where(self.hw.reference == hw_reference)
                .where(self.hw.student_id == student_id)
            )
            await connection.execute(str(query))
        finally:
            await connection.close()

    async def find_lesson(self, user_id: int):
        connection = await asyncpg.connect(**self.db_config)
        try:
            # Текущая дата и время
            now = datetime.now()
            # Время для уведомления - за 2 часа до занятия
            notification_time = now + timedelta(hours=2)

            query = (
                Query.from_(self.schedule)
                .select(self.schedule.date, self.schedule.topic)
                .where(self.schedule.student_id == user_id)
                .where(self.schedule.date[now:notification_time])
            )
            res = await connection.fetch(str(query))
            return res

        except Exception as e:
            logging.info(e)

        finally:
            await connection.close()


class MethodsForTeacher:
    def __init__(self, config):
        self.db_config = config
        self.users = Table("users")
        self.schedule = Table("schedule")
        self.hw = Table("homework")

    async def get_user_id(self, name: str) -> Optional[int]:
        connection = await asyncpg.connect(**self.db_config)
        try:
            query = (
                Query.from_(self.users)
                .select(self.users.user_id)
                .where(self.users.name == name)
            )
            res = await connection.fetchrow(str(query))
            if res:
                return res["user_id"]
            else:
                return None

        except Exception as e:
            logging.info(e)
            return None

        finally:
            await connection.close()

    async def add_user(self, info: Dict) -> str:
        connection = await asyncpg.connect(**self.db_config)
        try:
            # проверка уникальности элемента таблицы
            query_check_existing = (
                Query.from_(self.users)
                .select(self.users.user_id)
                .where(
                    (self.users.name == info["name"])
                    | (
                        (self.users.login == info["login"])
                        & (self.users.password == info["password"])
                    )
                )
            )
            res = await connection.fetch(str(query_check_existing))
            if res:
                return "Пользователь с таким именем или с парой логин-пароль существует"

            # добавление ученика
            query = (
                Query.into(self.users)
                .columns(
                    self.users.name,
                    self.users.login,
                    self.users.password,
                    self.users.status,
                )
                .insert(
                    info["name"],
                    info["login"],
                    info["password"],
                    info["status"],
                )
            )
            await connection.execute(str(query))
            return f"Пользователь {info['name']} успешно добавлен"

        except Exception as e:
            logging.info(e)
            return "Ошибка в обращении к базе данных\nПовторите позже"

        finally:
            await connection.close()

    async def remove_user(self, user_id: int, name_to_delete: str):
        connection = await asyncpg.connect(**self.db_config)
        try:
            # проверка существования пользователя
            query_existing = (
                Query.from_(self.users)
                .select(self.users.user_id)
                .where(self.users.name == name_to_delete)
            )
            res = await connection.fetchrow(str(query_existing))
            if not res:
                return "Пользователя не существует"

            if res["user_id"] == user_id:
                return "Вы пытаетесь удалить себя"

            # удаление пользователя
            query = (
                Query.from_(self.users)
                .delete()
                .where(self.users.name == name_to_delete)
            )
            await connection.execute(str(query))
            return "Пользователь успешно удален"

        except Exception as e:
            logging.info(e)
            return "Ошибка в обращение к базе данных\nПовторите позже"

        finally:
            await connection.close()

    async def add_hw(self, info: Dict):
        connection = await asyncpg.connect(**self.db_config)
        try:
            # поиск ученика
            user_id = await self.get_user_id(info["student name"])
            if not user_id:
                return "Ученика с таким именем не существует"

            # проверка уникальности пары ученик-дз
            query_existing_hw = (
                Query.from_(self.hw)
                .select(self.hw.hw_id)
                .where(
                    (self.hw.reference == info["reference"])
                    & (self.hw.student_id == user_id)
                )
            )
            res = await connection.fetch(str(query_existing_hw))
            if res:
                return "Данное дз уже создано для данного ученика"

            # добавление дз
            query = (
                Query.into(self.hw)
                .columns(
                    self.hw.topic,
                    self.hw.student_id,
                    self.hw.reference,
                    self.hw.deadline,
                    self.hw.status,
                )
                .insert(
                    info["topic"],
                    user_id,
                    info["reference"],
                    info["deadline"],
                    "not done",
                )
            )
            await connection.execute(str(query))
            return "Домашнее задание успешно добавлено"

        except Exception as e:
            logging.info(e)
            return "Ошибка в обращение к базе данных\nПовторите позже"

        finally:
            await connection.close()

    async def remove_hw(self, student_name: str, reference: str):
        connection = await asyncpg.connect(**self.db_config)
        try:
            user_id = await self.get_user_id(student_name)
            if not user_id:
                return "Ученика с таким именем не существует"

            # проверяем существование дз с определенной ссылкой
            query_existing_ref = (
                Query.from_(self.hw)
                .select(self.hw.hw_id)
                .where(
                    (self.hw.student_id == user_id)
                    & (self.hw.reference == reference)
                )
            )
            res = await connection.fetch(str(query_existing_ref))
            if not res:
                return "Несуществующая ссылка"

            # удаляем дз
            query = (
                Query.from_(self.hw)
                .delete()
                .where(
                    (self.hw.student_id == user_id)
                    & (self.hw.reference == reference)
                )
            )
            await connection.execute(str(query))
            return "Дз успешно удалено"

        except Exception as e:
            logging.info(e)
            return "Ошибка в обращение к базе данных\nПовторите позже"

        finally:
            await connection.close()

    async def set_hw_deadline(self, student_id: int, reference: str) -> None:
        connection = await asyncpg.connect(**self.db_config)
        try:
            # меняем статус дз в зависимости от сделано оно или нет
            query_done = (
                Query.update(self.hw)
                .where(self.hw.student_id == student_id)
                .where(self.hw.reference == reference)
                .where(self.hw.status == "done")
                .set(self.hw.status, "deadline, done")
            )
            query_not_done = (
                Query.update(self.hw)
                .where(self.hw.student_id == student_id)
                .where(self.hw.reference == reference)
                .where(self.hw.status == "not done")
                .set(self.hw.status, "deadline, not done")
            )
            await connection.execute(str(query_done))
            await connection.execute(str(query_not_done))

        except Exception as e:
            logging.info(e)

        finally:
            await connection.close()

    async def add_lesson(self, info: Dict) -> str:
        connection = await asyncpg.connect(**self.db_config)
        try:
            # проверка существования ученика
            student_id = await db.get_user_id(info["student_name"])
            if not student_id:
                return "Ученика с таким именем не существует"

            # проверка свободна ли дата
            date = info["date"]
            prev_time = date - timedelta(minutes=59)
            future_time = date + timedelta(minutes=59)
            query_check = (
                Query.from_(self.schedule)
                .select(self.schedule.schedule_id)
                .where(self.schedule.date[prev_time:future_time])
            )
            res = await connection.fetch(str(query_check))
            if res:
                return "Время занято:\nЕсть занятие в промежутке меньше 1 часа"

            # добавление урока
            query = (
                Query.into(self.schedule)
                .columns(
                    self.schedule.student_id,
                    self.schedule.teacher_id,
                    self.schedule.date,
                    self.schedule.topic,
                )
                .insert(
                    student_id, info["teacher_id"], info["date"], info["topic"]
                )
            )
            await connection.execute(str(query))
            return "Занятие успешно добавлено"

        except Exception as e:
            logging.info(e)
            return "Ошибка в обращение к базе данных\nПовторите позже"

        finally:
            await connection.close()

    async def remove_lesson(self, teacher_id: int, date: datetime) -> str:
        connection = await asyncpg.connect(**self.db_config)
        try:
            # проверка существования
            query_find = (
                Query.from_(self.schedule)
                .select(self.schedule.schedule_id)
                .where(self.schedule.date == date)
            )
            res = await connection.fetch(str(query_find))
            if not res:
                return "Урока в данное время не запланировано"

            # удаление
            query = (
                Query.from_(self.schedule)
                .delete()
                .where(self.schedule.date == date)
                .where(self.schedule.teacher_id == teacher_id)
            )
            await connection.execute(str(query))
            return "Урок успешно удален"

        except Exception as e:
            logging.info(e)
            return "Ошибка в обращение к базе данных\nПовторите позже"

        finally:
            await connection.close()

    async def get_future_lessons_for_teacher(self, teacher_id: int):
        connection = await asyncpg.connect(**self.db_config)
        try:
            query = (
                Query.from_(self.schedule)
                .join(self.users)
                .on(self.schedule.student_id == self.users.user_id)
                .select(
                    self.users.name,
                    self.schedule.date,
                    self.schedule.topic,
                )
                .where(self.schedule.teacher_id == teacher_id)
                .orderby(self.schedule.date, order=Order.asc)
                .limit(5)
            )
            res = await connection.fetch(str(query))
            return res

        except Exception as e:
            logging.info(e)
            return "Ошибка в обращение к базе данных\nПовторите позже"

        finally:
            await connection.close()

    async def get_hw_for_teacher(self, info: Dict):
        connection = await asyncpg.connect(**self.db_config)
        try:
            # проверка существования ученика
            student_id = await db.get_user_id(info["name"])
            if not student_id:
                return "Ученика с таким именем не существует"

            start = info["start"]
            end = info["end"]
            query = (
                Query.from_(self.hw)
                .join(self.users)
                .on(self.hw.student_id == self.users.user_id)
                .select(
                    self.users.name,
                    self.hw.topic,
                    self.hw.reference,
                    self.hw.deadline,
                    self.hw.status,
                )
                .where(self.users.name == info["name"])
                .where(self.hw.deadline[start:end])
                .orderby(self.hw.deadline, order=Order.asc)
                .limit(5)
            )
            res = await connection.fetch(str(query))
            return res

        except Exception as e:
            logging.info(e)
            return "Ошибка в обращении к базе данных\nПовторите позже"

        finally:
            await connection.close()


class Database(MethodsForStudent, MethodsForTeacher):
    def __init__(self, config):
        MethodsForStudent.__init__(self, config)


db = Database(DATABASE_CONFIG)
