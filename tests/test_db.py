import asyncio
import datetime
from unittest.mock import patch

import pytest
import psycopg2
from database.methods import Database
import random

# Конфигурация тестовой базы данных
TEST_DB_CONFIG = {
    "database": "test_db",
    "user": "postgres",
    "password": "Timuraka47",
    "host": "localhost",
    "port": "5432",
}


@pytest.fixture(scope="session")
def init_db():
    connection = psycopg2.connect(**TEST_DB_CONFIG)
    cursor = connection.cursor()
    try:
        # создание таблиц
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS users ( "
            "user_id SERIAL PRIMARY KEY, "
            "login TEXT, "
            "password TEXT, "
            "name TEXT, "
            "status TEXT )"
        )

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS homework ( "
            "hw_id SERIAL PRIMARY KEY, "
            "topic TEXT, "
            "student_id INTEGER, "
            "reference TEXT, "
            "deadline TIMESTAMP, "
            "status TEXT)"
        )

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS schedule ( "
            "schedule_id SERIAL PRIMARY KEY, "
            "student_id INTEGER, "
            "teacher_id INTEGER, "
            "date TIMESTAMP, "
            "topic TEXT, "
            "price INTEGER)"
        )

        # добавление данных в бд для тестов
        user_id = 1
        cursor.execute(
            "INSERT INTO users (user_id, name, login, password, status) "
            f"VALUES (1, 'test_name', 'test_login', 'test_password', 'student')"
        )

        cursor.execute(
            "INSERT INTO users (user_id, name, login, password, status) "
            f"VALUES (2, 'test_name2', 'test_login2', 'test_passwor2', 'teacher')"
        )

        cursor.execute(
            "INSERT INTO homework (hw_id, topic, student_id, reference, deadline, status) "
            f"VALUES (1, 'test_topic', {user_id}, 'test_reference', '2024-12-31 23:59', 'not done')"
        )

        cursor.execute(
            "INSERT INTO homework (hw_id, topic, student_id, reference, deadline, status) "
            f"VALUES (2, 'test_topic2', {user_id}, 'test_reference2', '2024-12-31 23:59', 'deadline, not done')"
        )

        cursor.execute(
            "INSERT INTO schedule (schedule_id, student_id, teacher_id, date, topic, price) "
            "VALUES (1, 1, 2, '2024-12-31 23:59', 'test_topic', 1500)"
        )
        connection.commit()
        yield

        # Очистка базы данных после завершения всех тестов

        cursor.execute("DROP TABLE IF EXISTS homework;")
        cursor.execute("DROP TABLE IF EXISTS schedule;")
        cursor.execute("DROP TABLE IF EXISTS users;")
        connection.commit()
    finally:
        cursor.close()
        connection.close()


@pytest.fixture
def test_db():
    test_db = Database(TEST_DB_CONFIG)
    return test_db


@pytest.mark.asyncio
async def test_find_user(init_db, test_db):
    # проверка нахождения существующего пользователя
    login = "test_login"
    password = "test_password"
    expected_result = 1
    result = await test_db.find_user(login, password)
    assert result["user_id"] == expected_result

    # проверка нахождения несуществующего пользователя
    login = "wrong_login"
    password = "wrong_password"
    result = await test_db.find_user(login, password)
    assert result["status"] == "User not found"


@pytest.mark.asyncio
async def test_get_future_events(init_db, test_db):
    # проверка получения запланированного занятия
    result = await test_db.get_future_events(1)
    assert len(result) == 1
    assert result[0]["name"] == "test_name2"


@pytest.mark.asyncio
async def test_get_homework(init_db, test_db):
    result = await test_db.get_homework(1)
    # проверка игнорирование дз с прошедшим дедлайном
    assert len(result) == 1
    assert result[0]["reference"] == "test_reference"


@pytest.mark.asyncio
async def test_get_name(init_db, test_db):
    # проверка существующего пользователя
    user_id = 1
    result = await test_db.get_name(user_id)
    expected_result = "test_name"
    assert result == expected_result

    # проверка несуществующего пользователя
    user_id = -1
    result = await test_db.get_name(user_id)
    assert result is None


@pytest.mark.asyncio
async def test_check_ref_hw(init_db, test_db):
    # проверка существующей ссылки на дз
    user_id = 1
    result = await test_db.check_ref_hw(user_id, "test_reference")
    assert result

    # проверка несуществующей ссылки на дз
    result = await test_db.check_ref_hw(user_id, "wrong_test_reference")
    assert not result


@pytest.mark.asyncio
async def test_set_status_done(init_db, test_db):
    await test_db.set_status_done(1, "test_reference")
    connection = psycopg2.connect(**TEST_DB_CONFIG)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM homework WHERE status = 'done'")
        hw_done = cursor.fetchone()
        assert hw_done is not None
    finally:
        cursor.close()
        connection.close()


@pytest.mark.asyncio
async def test_get_user_id(init_db, test_db):
    # нахождение существующего пользователя
    result = await test_db.get_user_id("test_name")
    assert result == 1

    # пользователя не существует
    result = await test_db.get_user_id("wrong_name")
    assert result is None


@pytest.mark.asyncio
async def test_get_future_lessons_for_teacher(init_db, test_db):
    result = await test_db.get_future_lessons_for_teacher(2)
    assert len(result) == 1


@pytest.mark.asyncio
async def test_get_stat_lessons(init_db, test_db):
    start = datetime.datetime(year=2024, month=12, day=1)
    finish = datetime.datetime(year=2025, month=12, day=1)
    result = await test_db.get_stat_lesson(2, start, finish)
    assert dict(result) == {
        "total_price": 1500,
        "unique_students": 1,
        "total_lessons": 1,
    }

    finish = datetime.datetime(year=2024, month=12, day=2)
    result = await test_db.get_stat_lesson(2, start, finish)
    assert dict(result) == {
        "total_price": None,
        "unique_students": 0,
        "total_lessons": 0,
    }


@pytest.mark.asyncio
async def test_get_stat_student(init_db, test_db):
    start = datetime.datetime(year=2024, month=12, day=1)
    finish = datetime.datetime(year=2025, month=12, day=1)
    result = await test_db.get_stat_student(1, start, finish)
    assert dict(result[0]) == {"status": "deadline, not done", "count": 1}
