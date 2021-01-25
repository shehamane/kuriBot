from aiogram.dispatcher.filters.state import StatesGroup, State


class UserInfo(StatesGroup):
    UsersList = State()
