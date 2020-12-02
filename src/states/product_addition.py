from aiogram.dispatcher.filters.state import StatesGroup, State


class ProductAddition(StatesGroup):
    NameRequest = State()
    DescriptionRequest = State()
    ImageRequest = State()
