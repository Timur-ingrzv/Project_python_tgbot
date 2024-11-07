import asyncio
from datetime import datetime
from typing import Dict

import asyncpg
from pypika import Table, Query
from config import DATABASE_CONFIG


class Database:
    def __init__(self):
        self.db_config = DATABASE_CONFIG
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
                .where((self.users.login == login) & (self.users.password == password))
            )

            # Получение одной строки
            res = await connection.fetchrow(str(query))

            # Возврат результата
            if not res:
                return {"status": "User not found"}
            else:
                return {"user_id": res["user_id"], "name": res["name"], "status": res["status"]}
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
                .select(self.users.name, self.schedule.date, self.schedule.topic)
                .where(self.schedule.date > now).where(self.schedule.student_id == user_id)
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
                .select(self.hw.topic, self.hw.reference, self.hw.deadline)
                .where(self.hw.status == "not done")
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
                .where(self.hw.status != "deadline")
            )
            res = await connection.fetch(str(query))
            return bool(res)
        finally:
            await connection.close()


db = Database()
print(asyncio.run(db.check_ref_hw(1, "test_reference")))
