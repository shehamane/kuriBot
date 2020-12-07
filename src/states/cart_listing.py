from aiogram.dispatcher.filters.state import StatesGroup, State


class CartListing(StatesGroup):
    CartWatching = State()
    ProductWatching = State()
    RecordChanging = State()
