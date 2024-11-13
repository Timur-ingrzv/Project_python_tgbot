from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from utils.states import ChangeUser, UserStatus
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
    if len(data) != 4 or not (
        "учитель" in data[3].lower() or "ученик" in data[3].lower()
    ):
        await message.answer(
            f"Неправильная информация о пользователе\n"
            f"Количество строк не равно 4 или "
            f"тип пользователя не ученик и не учитель"
        )
        return

    if any(el.strip() == "" for el in data):
        await message.answer(
            f"Неправильная информация о пользователе\n"
            f"Присутсвует пустая строка"
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
    await callback.message.answer(f"Введите имя пользователя для удаления")


@router.message(StateFilter(ChangeUser.removing_user))
async def remove_user(message: types.Message, state: FSMContext):
    await state.set_state(UserStatus.teacher)
    user_data = await state.get_data()
    user_name = message.text.strip()
    res = await db.remove_user(user_data["user_id"], user_name)
    await message.answer(res)
