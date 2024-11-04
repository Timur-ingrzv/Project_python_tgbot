from aiogram.fsm.state import StatesGroup, State


class Registration(StatesGroup):
    input_login = State()
    input_password = State()