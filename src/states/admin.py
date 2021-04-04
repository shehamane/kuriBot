from aiogram.dispatcher.filters.state import StatesGroup, State


class AdminPanel(StatesGroup):
    AdminPanel = State()


class UserInfo(StatesGroup):
    UsersList = State()
    OrdersList = State()
    OrderInfo = State()


class CatalogEdit(StatesGroup):
    CategoryChoosing = State()
    ProductsWatching = State()
    CatalogImageRequest = State()
    CategoryNameRequest = State()
    CategoryDeletionConfirmation = State()
    ProductInfoRequest = State()
    ProductImageWaiting = State()
    ProductImageRequest = State()
    ProductWatching = State()
    ProductDeletionConfirmation = State()
    ProductInfoChangeRequest = State()
    ProductImageChangeRequest = State()
