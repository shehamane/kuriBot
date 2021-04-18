from aiogram.dispatcher.filters.state import StatesGroup, State


class Cart(StatesGroup):
    CartItems = State()
    ItemInfo = State()
    ClearConfirmation = State()
