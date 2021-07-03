from aiogram.dispatcher.filters.state import StatesGroup, State


class AdminPanel(StatesGroup):
    AdminPanel = State()


class Settings(StatesGroup):
    Menu = State()
    CatalogImageRequest = State()
    CartImageRequest = State()


class UserInfo(StatesGroup):
    UsersList = State()
    OrdersList = State()
    OrderInfo = State()


class AdminCatalog(StatesGroup):
    Categories = State()
    EmptyCategory = State()
    Products = State()
    CatalogImageRequest = State()
    CategoryNameRequest = State()
    CategoryDeletionConfirmation = State()
    ProductInfoRequest = State()
    ProductImageRequest = State()
    ProductInfo = State()
    ProductDeletionConfirmation = State()
    ProductInfoChangeRequest = State()
    ProductImageChangeRequest = State()
    CatalogClearingConfirmation = State()
    CategoryNewNameRequest = State()
