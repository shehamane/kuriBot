from aiogram.dispatcher.filters.state import StatesGroup, State


class Catalog(StatesGroup):
    Categories = State()
    Product = State()
