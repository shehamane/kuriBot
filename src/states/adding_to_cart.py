from aiogram.dispatcher.filters.state import StatesGroup, State


class AddingToCart(StatesGroup):
    NumberRequest = State()
