from aiogram.dispatcher.filters.state import StatesGroup, State


class ProductRemoving(StatesGroup):
    NameRequest = State()
