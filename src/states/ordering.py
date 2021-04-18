from aiogram.dispatcher.filters.state import StatesGroup, State


class Ordering(StatesGroup):
    OrderConfirmation = State()
    Payment = State()
