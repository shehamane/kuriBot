from aiogram.dispatcher.filters.state import StatesGroup, State


class CatalogListing(StatesGroup):
    CategoryChoosing = State()
    ProductWatching = State()
