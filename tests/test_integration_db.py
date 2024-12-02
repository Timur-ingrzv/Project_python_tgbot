import asyncio
import time
from random import random

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
        cursor.execute("CREATE TABLE IF NOT EXISTS users ( "
                       "user_id SERIAL PRIMARY KEY, "
                       "login TEXT, "
                       "password TEXT, "
                       "name TEXT, "
                       "status TEXT )")

        cursor.execute("CREATE TABLE IF NOT EXISTS homework ( "
                       "hw_id SERIAL PRIMARY KEY, "
                       "topic TEXT, "
                       "student_id INTEGER, "
                       "reference TEXT, "
                       "deadline TIMESTAMP, "
                       "status TEXT)")

        # добавление данных в бд для тестов
        user_id = 1
        cursor.execute("INSERT INTO users (user_id, name, login, password) "
                       f"VALUES ({user_id}, 'test_name', 'test_login', 'test_password')")

        cursor.execute("INSERT INTO homework (hw_id, topic, student_id, reference, deadline, status) "
                       f"VALUES (1, 'test_topic', {user_id}, 'test_reference', '2024-12-31 23:59', 'test_status')")
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
    """проверка метода find_user"""

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
async def test_get_name(init_db, test_db):
    '''проверка метода get_name'''
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
    '''Проверка метода check_ref_hw'''
    # проверка существующей ссылки на дз
    user_id = 1
    result = await test_db.check_ref_hw(user_id, "test_reference")
    assert result

    # проверка несуществующей ссылки на дз
    result = await test_db.check_ref_hw(user_id, "wrong_test_reference")
    assert not result


@pytest.mark.asyncio
async def test_set_status_done(init_db, test_db):
    '''проверка метода set_status_done'''
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
