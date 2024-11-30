import datetime

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from database.methods import Database
from pypika import Table


@pytest.fixture(scope="function")
def connection():
    mock_connection = MagicMock()
    mock_connection.close = AsyncMock()
    return mock_connection


@pytest.fixture(scope="function")
def db():
    config = {}
    instance = Database(config)
    return instance


@pytest.mark.asyncio
async def test_find_user_success(db, connection):
    connection.fetchrow = AsyncMock(
        return_value={"user_id": 1, "name": "John", "status": "active"}
    )
    with patch("asyncpg.connect", AsyncMock(return_value=connection)):
        result = await db.find_user("test_login", "test_password")
        assert result == {"user_id": 1, "name": "John", "status": "active"}


@pytest.mark.asyncio
async def test_find_user_not_found(db, connection):
    connection.fetchrow = AsyncMock(return_value=None)
    # Патч подключения к базе данных
    with patch("asyncpg.connect", AsyncMock(return_value=connection)):
        result = await db.find_user("test_login", "test_password")
        assert result["status"] == "User not found"


@pytest.mark.asyncio
async def test_get_future_events(db, connection):
    connection.fetch = AsyncMock(
        return_value=[
            {
                "name": "test_name",
                "date": datetime.datetime(day=11, year=2024, month=11),
                "topic": "test_topic",
            }
        ]
    )
    with patch("asyncpg.connect", AsyncMock(return_value=connection)):
        result = await db.get_future_events(1)
        assert result[0]["name"] == "test_name"
        assert result[0]["topic"] == "test_topic"


@pytest.mark.asyncio
async def test_get_name(db, connection):
    with patch("asyncpg.connect", AsyncMock(return_value=connection)):
        connection.fetchrow = AsyncMock(return_value={"name": "test_name"})
        result = await db.get_name(1)
        assert result == "test_name"

        connection.fetchrow = AsyncMock(return_value=None)
        result = await db.get_name(1)
        assert result is None


@pytest.mark.asyncio
async def test_check_ref_hw(db, connection):
    with patch("asyncpg.connect", AsyncMock(return_value=connection)):
        connection.fetch = AsyncMock(return_value={"id": "1"})
        result = await db.check_ref_hw(1, "test_ref")
        assert result

        connection.fetch = AsyncMock(return_value=None)
        result = await db.check_ref_hw(1, "test_ref")
        assert not result


@pytest.mark.asyncio
async def test_find_lesson(db, connection):
    with patch("asyncpg.connect", AsyncMock(return_value=connection)):
        connection.fetch = AsyncMock(
            return_value={"date": datetime.date, "topic": "test_topic"}
        )
        result = await db.find_lesson(1)
        assert result == {"date": datetime.date, "topic": "test_topic"}

        connection.fetch = AsyncMock(return_value=None)
        result = await db.find_lesson(1)
        assert not result
