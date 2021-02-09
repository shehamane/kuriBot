from aiogram.dispatcher.filters.state import StatesGroup, State


class AdminPanel(StatesGroup):
    AdminPanel = State()


class UserInfo(StatesGroup):
    UsersList = State()


class CatalogEdit(StatesGroup):
    CategoryChoosing = State()
    ProductsWatching = State()
    CatalogImageRequest = State()
    CategoryNameRequest = State()
    DeletionConfirmation = State()
