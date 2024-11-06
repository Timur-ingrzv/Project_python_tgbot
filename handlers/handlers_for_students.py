from aiogram import F, Router, types
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from database.methods import db
from utils.states import SendingHw, UserStatus

router = Router()


@router.callback_query(F.data == "exit profile")
async def exit_profile(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    message = types.Message(
        message_id=callback.message.message_id,
        from_user=callback.from_user,
        chat=callback.message.chat,
        date=callback.message.date,
        text="/start",
    )
    from bot import cmd_start, bot

    await cmd_start(message, bot)


@router.callback_query(F.data == "show schedule")
async def show_schedule(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    res = await db.get_future_events(user_data["user_id"])
    if res:
        for el in res:
            await callback.message.answer(
                f"<b>Дата:</b> {el['date']}\n"
                f"<b>Учитель:</b> {el['name']}\n"
                f"<b>Тема:</b> {el['topic']}\n\n"
            )
    else:
        await callback.message.answer(f"У вас нет запланированных занятий")


@router.callback_query(F.data == "show hw")
async def show_hw(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    res = await db.get_homework(user_data["user_id"])
    if res:
        for hw in res:
            await callback.message.answer(
                f"<b>Тема:</b> {hw['topic']}\n"
                f"<b>Ссылка на дз:</b> {hw['reference']}\n"
                f"<b>Дедлайн:</b> {hw['deadline']}\n"
            )
    else:
        await callback.message.answer(f"У вас нет домашнего задания.\nМожете отдыхать!")


@router.callback_query(F.data == "send hw")
async def input_link(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите ссылку на домашнее задание")
    await state.set_state(SendingHw.waiting_for_link)


@router.message(StateFilter(SendingHw.waiting_for_link))
async def input_file(message: types.Message, state: FSMContext):
    await state.update_data(link=message.text)
    await message.answer("Загрузите файл")
    await state.set_state(SendingHw.waiting_for_file)


@router.message(StateFilter(SendingHw.waiting_for_file))
async def send_hw(message: types.Message, state: FSMContext):
    await state.set_state(UserStatus.student)
    if message.document:
        await message.answer("Домашнее задание отправлено")
    else:
        await message.answer("Неправильный формат файла или неправильная ссылка")
