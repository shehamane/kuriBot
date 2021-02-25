from aiogram.dispatcher.filters.state import StatesGroup, State


class Orders(StatesGroup):
    OrderList = State()
    OrderInfo = State()