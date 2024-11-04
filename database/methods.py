from typing import Dict

import asyncpg
from pypika import Table, Query
from config import DATABASE_CONFIG


class Database:
    def __init__(self):
        self.db_config = DATABASE_CONFIG
        self.data_base_url = (
            f"postgresql://"
            f"{self.db_config['user']}:{self.db_config['password']}"
            f"@{self.db_config['host']}:{self.db_config['port']}/"
            f"{self.db_config['dbname']}"
        )
        self.users = Table("users")

    async def find_user(self, login: str, password: str) -> Dict:
        connection = await asyncpg.connect(self.data_base_url)
        try:
            # Создание запроса с использованием Pypika
            query = (
                Query.from_(self.users)
                .select(self.users.name, self.users.status)
                .where((self.users.login == login) & (self.users.password == password))
            )

            # Выполнение асинхронного запроса и получение одной строки
            res = await connection.fetchrow(str(query))

            # Возврат результата
            if not res:
                return {"status": "User not found"}
            else:
                return {"name": res["name"], "status": res["status"]}
        finally:
            # Закрытие соединения
            await connection.close()


db = Database()
