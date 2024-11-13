from aiogram.fsm.state import StatesGroup, State


class Registration(StatesGroup):
    input_login = State()
    input_password = State()


class UserStatus(StatesGroup):
    student = State()
    teacher = State()


class SendingHw(StatesGroup):
    waiting_for_link = State()
    waiting_for_file = State()


class ChangeUser(StatesGroup):
    adding_user = State()
    removing_user = State()
