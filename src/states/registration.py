from aiogram.dispatcher.filters.state import StatesGroup, State


class Registration(StatesGroup):
    Menu = State()
    NameRequest = State()
    PhoneRequest = State()
    AddressRequest = State()
    FinishCheck = State()