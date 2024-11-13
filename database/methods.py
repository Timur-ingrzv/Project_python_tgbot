import asyncio
from datetime import datetime, timedelta
from typing import Dict

import asyncpg
from pypika import Table, Query
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
                .where(self.hw.status != "Deadline")
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
                .set(self.hw.status, "Done")
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
        finally:
            await connection.close()


class MethodsForTeacher:
    def __init__(self, config):
        self.db_config = config
        self.users = Table("users")
        self.schedule = Table("schedule")
        self.hw = Table("homework")

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
        finally:
            await connection.close()


class Database(MethodsForStudent, MethodsForTeacher):
    def __init__(self, config):
        MethodsForStudent.__init__(self, config)


db = Database(DATABASE_CONFIG)
