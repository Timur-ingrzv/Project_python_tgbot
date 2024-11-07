import aiohttp
from aiogram import F, Router, types
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from database.methods import db
from utils.states import SendingHw, UserStatus
from utils.func_for_files import upload_to_yandex_disk

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
        await callback.message.answer(
            f"У вас нет домашнего задания.\nМожете отдыхать!"
        )


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
    user_data = await state.get_data()
    # проверка формата файла и существование ссылки на дз
    if message.document and message.document.mime_type == "application/pdf" and db.check_ref_hw(user_data["user_id"],
                                                                                                user_data["link"]):
        from bot import bot
        from config import TOKEN

        file_id = message.document.file_id
        file_name = message.document.file_name

        # получаем файл
        file_info = await bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.get(file_url) as file_response:
                # проверяем статус запроса
                if file_response.status == 200:
                    file_data = await file_response.read()
                    student_name = db.get_name(user_data["user_id"])
                    # загружаем файл на яндекс диск
                    result = await upload_to_yandex_disk(file_data, file_name, student_name)

                    await message.answer(f"{result}")
                else:
                    await message.answer("Не удалось загрузить файл из Telegram\n"
                                        "Попробуйте повторить позже")

    else:
        await message.answer(
            "Неправильный формат файла или неправильная ссылка"
        )
