from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from keyboards.default.admin_panel import settings_kb
from keyboards.inline import cancel_kb
from loader import dp

from states import AdminPanel, AdminCatalog, UserInfo
from states.admin import Settings
from utils.misc.files import download_image


@dp.message_handler(Text(ignore_case=True, contains=["настройки"]),
                    state=[AdminPanel.AdminPanel, AdminCatalog.Categories, UserInfo.OrderInfo,
                           UserInfo.UsersList, UserInfo.OrdersList])
async def show_settings(message: Message, state: FSMContext):
    await state.finish()
    await message.answer("Настройки магазина:", reply_markup=settings_kb)
    await Settings.Menu.set()


@dp.message_handler(Text(equals=["Изображение каталога"]), state=[Settings.Menu])
async def ask_catalog_image(message: Message):
    await message.answer("Отправьте новое изображение", reply_markup=cancel_kb)
    await Settings.CatalogImageRequest.set()


@dp.message_handler(Text(equals=["Изображение корзины"]), state=[Settings.Menu])
async def ask_catalog_image(message: Message):
    await message.answer("Отправьте новое изображение", reply_markup=cancel_kb)
    await Settings.CartImageRequest.set()


@dp.message_handler(content_types=['photo'], state=Settings.CatalogImageRequest)
async def change_catalog_image(message: Message):
    await download_image("catalog.png", message.photo[-1])
    await message.answer("Изображение каталога успешно изменено!", reply_markup=settings_kb)
    await Settings.Menu.set()


@dp.message_handler(content_types=['photo'], state=Settings.CartImageRequest)
async def change_catalog_image(message: Message):
    await download_image("cart.png", message.photo[-1])
    await message.answer("Изображение корзины успешно изменено!", reply_markup=settings_kb)
    await Settings.Menu.set()


@dp.callback_query_handler(text="cancel", state=[Settings.CartImageRequest, Settings.CatalogImageRequest])
async def cancel_operation(call: CallbackQuery):
    await call.message.answer("Отмена изменений", reply_markup=settings_kb)
    await Settings.Menu.set()