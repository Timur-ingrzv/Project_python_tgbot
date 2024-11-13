from datetime import datetime

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from utils.states import ChangeUser, UserStatus, ChangeHw
from database.methods import db

router = Router()


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

    # проверка корректности данных
    if len(data) != 4:
        await message.answer(
            "Неправильная информация о пользователе\n"
            "Количество строк не равно 4"
        )
        return

    if not ("учитель" in data[3].lower() or "ученик" in data[3].lower()):
        await message.answer(
            "Неправильная информация о пользователе\n"
            "Тип пользователя не ученик и не учитель"
        )
        return

    if any(el.strip() == "" for el in data):
        await message.answer(
            "Неправильная информация о пользователе\n"
            "Присутствует пустая строка"
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
        "'Время сдачи в формате dd-mm-yyyy hours'\n"
    )


@router.message(StateFilter(ChangeHw.adding_hw))
async def add_hw(message: types.Message, state: FSMContext):
    await state.set_state(UserStatus.teacher)
    data = message.text.split("\n")

    # проверка корректности информации о дз
    if len(data) != 4:
        await message.answer(
            "Неправильная информация о дз:\n" "Количество строк не равно 4"
        )
        return

    if any(el.strip() == "" for el in data):
        await message.answer(
            "Неправильная информация о дз:\n" "Присутсвует пустая строка"
        )
        return

    try:
        valid_date = datetime.strptime(data[3], "%d-%m-%Y %H")
    except Exception:
        await message.answer(
            "Неправильная информация о дз:\n" "Неправильный формат даты"
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
    await message.answer(res)


@router.callback_query(F.data == "remove hw")
async def waiting_for_info_to_remove_hw(
    callback: types.CallbackQuery, state: FSMContext
):
    await state.set_state(ChangeHw.removing_hw)
    await callback.message.answer(
        "Введите данные о домашнем задании в формате для удаления:\n"
        "'Имя ученика'\n"
        "'Ссылка на дз'\n"
    )


@router.message(StateFilter(ChangeHw.removing_hw))
async def remove_hw(message: types.Message, state: FSMContext):
    await state.set_state(UserStatus.teacher)
    data = message.text.split("\n")

    # проверка корректности данных
    if len(data) != 2:
        await message.answer(
            "fНеправильная информация о дз:\n" f"Количество строк не равно 2"
        )
        return

    if any(el.strip() == "" for el in data):
        await message.answer(
            "fНеправильная информация о дз:\n" f"Присутствует пустая строка"
        )
        return

    student_name = data[0].strip()
    hw_reference = data[1].strip()
    res = await db.remove_hw(student_name, hw_reference)
    await message.answer(res)
