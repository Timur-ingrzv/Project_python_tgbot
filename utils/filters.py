from aiogram.filters.command import Filter
from aiogram import types
from enum import Enum


class UserStatus(Enum):
    TEACHER = "administration"
    STUDENT = "client"
    UNAUTHORIZED_USER = "unauthorized"


class IsTeacherFilter(Filter):
    async def __call__(self, message: types.Message, user_status: UserStatus) -> bool:
        return user_status == UserStatus.TEACHER


class IsStudentFilter(Filter):
    async def __call__(self, message: types.Message, user_status: UserStatus) -> bool:
        return user_status == UserStatus.STUDENT
