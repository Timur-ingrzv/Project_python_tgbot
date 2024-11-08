from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot import cmd_start
from utils import states
from database.methods import db

router = Router()


@router.callback_query(StateFilter(None), F.data == "authorization")
async def enter_login(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите логин")
    await state.set_state(states.Registration.input_login)


@router.message(StateFilter(states.Registration.input_login))
async def enter_password(message: types.Message, state: FSMContext):
    await state.update_data(login=message.text)
    await message.answer("Введите пароль")
    await state.set_state(states.Registration.input_password)


@router.message(StateFilter(states.Registration.input_password))
async def authorization(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    res = await db.find_user(user_data["login"], message.text)
    if res["status"] == "User not found":
        await message.answer("Неверный логин или пароль\nПопробуйте еще раз")
        await state.set_state(None)

        fake_callback = types.CallbackQuery(
            id="retry_authorization",
            from_user=message.from_user,
            message=message,
            data="authorization",
            chat_instance=str(message.chat.id),
        )

        await enter_login(fake_callback, state)
    else:
        await state.set_state(None)
        await message.answer(f"С возвращением, {res['name']}")


@router.message()
async def wrong_message(message: types.Message):
    await message.answer("Я не понимаю, используй кнопки или напиши /start")