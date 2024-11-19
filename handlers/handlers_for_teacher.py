import asyncio
from datetime import datetime
from typing import List

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from utils.scheduler import scheduler_set_deadline
from utils.states import ChangeUser, UserStatus, ChangeHw, ChangeLesson
from database.methods import db

router = Router()


def check_valid_data(data: List, length: int) -> str:
    if len(data) != length:
        return (
            f"Неправильная информация:\n" f"Количество строк не равно {length}"
        )

    if any(el.strip() == "" for el in data):
        return "Неправильная информация о дз:\n" "Присутствует пустая строка"
    return "ok"


@router.callback_query(F.data == "add user")
async def waiting_for_info_to_add_user(
    callback: types.CallbackQuery, state: FSMContext
):
    await state.set_state(ChangeUser.adding_user)
    await callback.message.answer(
        f"Введите данные пользователя в формате:\n"
        f"'Имя'\n"
        f"'Логин'\n"
        f"'Пароль'\n"
        f"'Ученик' или 'Учитель'"
    )


@router.message(StateFilter(ChangeUser.adding_user))
async def add_user(message: types.Message, state: FSMContext):
    await state.set_state(UserStatus.teacher)
    data = message.text.split("\n")

    # проверка корректности данных об ученике
    checker_res = check_valid_data(data, 4)
    if checker_res != "ok":
        await message.answer(checker_res)
        return

    if not ("учитель" in data[3].lower() or "ученик" in data[3].lower()):
        await message.answer(
            "Неправильная информация о пользователе\n"
            "Тип пользователя не ученик и не учитель"
        )
        return

    # добавление ученика в базу данных
    info = {
        "name": data[0].strip(),
        "login": data[1].strip(),
        "password": data[2].strip(),
        "status": "student" if "ученик" in data[3].lower() else "teacher",
    }
    res = await db.add_user(info)
    await message.answer(res)


@router.callback_query(F.data == "remove user")
async def waiting_for_info_to_remove_user(
    callback: types.CallbackQuery, state: FSMContext
):
    await state.set_state(ChangeUser.removing_user)
    await callback.message.answer("Введите имя пользователя для удаления")


@router.message(StateFilter(ChangeUser.removing_user))
async def remove_user(message: types.Message, state: FSMContext):
    await state.set_state(UserStatus.teacher)
    user_data = await state.get_data()
    user_name = message.text.strip()
    res = await db.remove_user(user_data["user_id"], user_name)
    await message.answer(res)


@router.callback_query(F.data == "add hw")
async def waiting_for_info_to_add_hw(
    callback: types.CallbackQuery, state: FSMContext
):
    await state.set_state(ChangeHw.adding_hw)
    await callback.message.answer(
        "Введите данные о домашнем задании в формате:\n"
        "'Тема'\n"
        "'Имя ученика'\n"
        "'\Ссылка на дз'\n"
        "'Время сдачи в формате dd-mm-yyyy hours:minutes'\n"
    )


@router.message(StateFilter(ChangeHw.adding_hw))
async def add_hw(message: types.Message, state: FSMContext):
    await state.set_state(UserStatus.teacher)
    data = message.text.split("\n")

    # проверка корректности информации о дз
    checker_res = check_valid_data(data, 4)
    if checker_res != "ok":
        await message.answer(checker_res)
        return

    try:
        valid_date = datetime.strptime(data[3], "%d-%m-%Y %H:%M")
    except Exception:
        await message.answer(
            "Неправильная информация о дз:\n" "Неправильный формат даты"
        )
        return

    if valid_date < datetime.now():
        await message.answer(
            "Неправильное время дедлайна:\n" "Раньше текущего времени"
        )
        return

    # добавление дз в базу данных
    info = {
        "topic": data[0].strip(),
        "student name": data[1].strip(),
        "reference": data[2].strip(),
        "deadline": valid_date,
    }

    res = await db.add_hw(info)

    # создаем отложенную таску для изменения статуса на дедлайн
    if "успешно добавлено" in res:
        delta = valid_date - datetime.now()
        t_1 = asyncio.create_task(
            scheduler_set_deadline(
                delta, info["student name"], info["reference"]
            )
        )
    await message.answer(res)


@router.callback_query(F.data == "remove hw")
async def waiting_for_info_to_remove_hw(
    callback: types.CallbackQuery, state: FSMContext
):
    await state.set_state(ChangeHw.removing_hw)
    await callback.message.answer(
        "Введите данные о домашнем задании для удаления в формате:\n"
        "'Имя ученика'\n"
        "'Ссылка на дз'\n"
    )


@router.message(StateFilter(ChangeHw.removing_hw))
async def remove_hw(message: types.Message, state: FSMContext):
    await state.set_state(UserStatus.teacher)
    data = message.text.split("\n")

    # проверка корректности данных о дз
    checker_res = check_valid_data(data, 2)
    if checker_res != "ok":
        await message.answer(checker_res)
        return

    student_name = data[0].strip()
    hw_reference = data[1].strip()
    res = await db.remove_hw(student_name, hw_reference)
    await message.answer(res)


@router.callback_query(F.data == "add lesson")
async def waiting_for_info_to_add_lesson(
    callback: types.CallbackQuery, state: FSMContext
):
    await state.set_state(ChangeLesson.adding_lesson)
    await callback.message.answer(
        f"Введите данные об уроке в формате:\n"
        f"'Имя ученика'\n"
        f"'Тема урока'\n"
        f"'Время урока в формате dd-mm-yyyy hours:minutes'"
    )


@router.message(StateFilter(ChangeLesson.adding_lesson))
async def add_lesson(message: types.Message, state: FSMContext):
    await state.set_state(UserStatus.teacher)
    data = message.text.split("\n")

    # проверка корректности информации об уроке
    checker_res = check_valid_data(data, 3)
    if checker_res != "ok":
        await message.answer(checker_res)
        return

    try:
        valid_date = datetime.strptime(data[2], "%d-%m-%Y %H:%M")
    except Exception:
        await message.answer(
            "Неправильная информация об уроке:\n" "Неправильный формат даты"
        )
        return

    if valid_date < datetime.now():
        await message.answer(
            "Неправильное время урока:\n" "Раньше текущего времени"
        )
        return

    # добавление урока
    user_data = await state.get_data()
    info = {
        "student_name": data[0].strip(),
        "topic": data[1].strip(),
        "date": valid_date,
        "teacher_id": user_data["user_id"],
    }
    res = await db.add_lesson(info)
    await message.answer(res)
