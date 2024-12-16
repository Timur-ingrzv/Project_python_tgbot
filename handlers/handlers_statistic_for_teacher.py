import asyncio
from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram import F, Router, types

from database.methods import db
from handlers.handlers_for_teacher import check_valid_data
from keyboards.keyboards_for_teacher import get_interface_for_statistic
from utils.states import Statistic, UserStatus

router = Router()


@router.callback_query(F.data == "get statistic interface")
async def show_statistic_interface(callback: types.CallbackQuery):
    await callback.message.answer(
        "Доступные команды для отображения статистики:",
        reply_markup=get_interface_for_statistic(),
    )


@router.callback_query(F.data == "statistic for lessons")
async def waiting_for_info_to_show_stat_lesson(
    callback: types.CallbackQuery, state: FSMContext
):
    await state.set_state(Statistic.stat_lessons)
    await callback.message.answer(
        "Введите данные в формате:\n"
        f"'Начало промежутка в формате dd-mm-yyyy hours:minutes'\n"
        f"'Конец промежутка в формате dd-mm-yyyy hours:minutes'"
    )


@router.message(StateFilter(Statistic.stat_lessons))
async def show_stat_lesson(message: types.Message, state: FSMContext):
    await state.set_state(UserStatus.teacher)
    data = message.text.split("\n")

    # проверка корректности информации о дз
    checker_res = check_valid_data(data, 2)
    if checker_res != "ok":
        await message.answer(checker_res)
        return

    try:
        valid_date_start = datetime.strptime(data[0].strip(), "%d-%m-%Y %H:%M")
        valid_date_finish = datetime.strptime(data[1].strip(), "%d-%m-%Y %H:%M")
    except Exception:
        await message.answer("Неправильный формат даты")
        return
    if valid_date_start > valid_date_finish:
        await message.answer("Начало промежутка должно быть раньше конца")
        return

    # статистика
    user_data = await state.get_data()
    teacher_id = user_data["user_id"]
    res = await db.get_stat_lesson(
        teacher_id, valid_date_start, valid_date_finish
    )
    if isinstance(res, str):
        await message.answer(res)
        return

    await message.answer(
        f"<b>Доход:</b> {res['total_price'] if res['total_price'] is not None else 0}\n"
        f"<b>Количество занятий:</b> {res['total_lessons']}\n"
        f"<b>Количество учеников:</b> {res['unique_students']}"
    )


@router.callback_query(F.data == "statistic for student")
async def waiting_for_info_to_show_stat_lesson(
    callback: types.CallbackQuery, state: FSMContext
):
    await state.set_state(Statistic.stat_student)
    await callback.message.answer(
        "Введите данные в формате:\n"
        "'Имя ученика'\n"
        f"'Начало промежутка в формате dd-mm-yyyy hours:minutes'\n"
        f"'Конец промежутка в формате dd-mm-yyyy hours:minutes'"
    )


@router.message(StateFilter(Statistic.stat_student))
async def show_stat_student(message: types.Message, state: FSMContext):
    await state.set_state(UserStatus.teacher)
    data = message.text.split("\n")
    # проверка корректности информации о дз
    checker_res = check_valid_data(data, 3)
    if checker_res != "ok":
        await message.answer(checker_res)
        return

    try:
        valid_date_start = datetime.strptime(data[1].strip(), "%d-%m-%Y %H:%M")
        valid_date_finish = datetime.strptime(data[2].strip(), "%d-%m-%Y %H:%M")
    except Exception:
        await message.answer("Неправильный формат даты")
        return
    if valid_date_start > valid_date_finish:
        await message.answer("Начало промежутка должно быть раньше конца")
        return
    student_name = data[0]

    # статистика
    student_id = await db.get_user_id(student_name)
    if not student_id:
        await message.answer("Ученика с таким именем не существует")
        return

    res = await db.get_stat_student(
        student_id, valid_date_start, valid_date_finish
    )
    statistic = ""
    for el in res:
        count = el["count"]
        if el["status"] == "done":
            status = "Сделано до дедлайна"
        elif el["status"] == "not done":
            status = "Еще не сделано"
        elif el["status"] == "deadline, done":
            status = "Сделано, дедлайн прошел"
        else:
            status = "Не сделано, дедлайн прошел"
        statistic += f"<b>{status}:</b> {count}\n"

    if statistic == "":
        statistic = "Ни одно дз не стоит на эти даты"

    await message.answer(statistic)


@router.message()
async def unknown_message(message: types.Message):
    await message.answer(
        "Я не понимаю, напишите /help и(или) используйте кнопки"
    )
