from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from keyboards.default.admin_panel import settings_kb, appearance_settings_kb, payment_settings_kb
from keyboards.inline import cancel_kb, confirmation_cancel_kb
from keyboards.inline.delivery_methods import get_delivery_kb
from keyboards.inline.payment_methods import payment_method_kb
from loader import dp
from utils.callback_datas import choose_delivery_method_cd
from utils.db_api.api import db_api as db

from states import AdminPanel, AdminCatalog, UserInfo
from states.admin import Settings
from utils.misc.files import download_image
import utils.misc.config_writer


@dp.message_handler(Text(ignore_case=True, contains=["настройки"]),
                    state=[AdminPanel.AdminPanel, AdminCatalog.Categories, UserInfo.OrderInfo,
                           UserInfo.UsersList, UserInfo.OrdersList])
async def show_settings_menu(message: Message, state: FSMContext):
    await state.finish()
    await message.answer("Настройки магазина:", reply_markup=settings_kb)
    await Settings.Menu.set()


@dp.message_handler(Text(equals="Назад"), state=[Settings.AppearanceMenu, Settings.PaymentMenu])
async def back_to_menu(message: Message, state: FSMContext):
    await show_settings_menu(message, state)


#                          APPEARANCE SETTINGS

@dp.message_handler(Text(equals="Внешний вид"), state=Settings.Menu)
async def show_appearance_settings(message: Message):
    await message.answer("Настройки внешнего вида:", reply_markup=appearance_settings_kb)
    await Settings.AppearanceMenu.set()


@dp.message_handler(Text(equals=["Изображение каталога"]), state=Settings.AppearanceMenu)
async def ask_catalog_image(message: Message):
    await message.answer("Отправьте новое изображение", reply_markup=cancel_kb)
    await Settings.CatalogImageRequest.set()


@dp.message_handler(Text(equals=["Изображение корзины"]), state=Settings.AppearanceMenu)
async def ask_catalog_image(message: Message):
    await message.answer("Отправьте новое изображение", reply_markup=cancel_kb)
    await Settings.CartImageRequest.set()


@dp.message_handler(content_types=['photo'], state=Settings.CatalogImageRequest)
async def change_catalog_image(message: Message):
    await download_image("catalog.png", message.photo[-1])
    await message.answer("Изображение каталога успешно изменено!", reply_markup=settings_kb)
    await Settings.AppearanceMenu.set()


@dp.message_handler(content_types=['photo'], state=Settings.CartImageRequest)
async def change_catalog_image(message: Message):
    await download_image("cart.png", message.photo[-1])
    await message.answer("Изображение корзины успешно изменено!", reply_markup=settings_kb)
    await Settings.AppearanceMenu.set()


@dp.callback_query_handler(text="cancel", state=[Settings.CartImageRequest, Settings.CatalogImageRequest])
async def cancel_operation(call: CallbackQuery):
    await call.message.answer("Отмена изменений", reply_markup=appearance_settings_kb)
    await Settings.AppearanceMenu.set()


#                    PAYMENT SETTINGS


@dp.message_handler(Text(equals="Оплата"), state=Settings.Menu)
async def show_payment_settings(message: Message):
    await message.answer("Настройки оплаты:", reply_markup=payment_settings_kb)
    await Settings.PaymentMenu.set()


@dp.message_handler(Text(equals="Способы доставки"), state=[Settings.PaymentMenu, Settings.PaymentMethods])
async def show_delivery_methods_list(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["main_message"] = await message.answer("Чтобы удалить способ доставки, нажмите на него",
                                                    reply_markup=await get_delivery_kb(
                                                        await db.get_delivery_methods_list()))
    await Settings.DeliveryMethods.set()


@dp.callback_query_handler(text="new_method", state=Settings.DeliveryMethods)
async def get_method_info(call: CallbackQuery):
    await call.message.edit_text("Введите информацию о методе доставки по шаблону НАЗВАНИЕ$ЦЕНА",
                                 reply_markup=cancel_kb)
    await Settings.DeliveryMethodInfoRequest.set()


@dp.message_handler(state=Settings.DeliveryMethodInfoRequest)
async def create_method(message: Message, state: FSMContext):
    strings = message.text.split('$')
    async with state.proxy() as data:
        if len(strings) != 2 or not strings[1].isnumeric():
            await data["main_message"].edit_text(
                "Вы неверно ввели информацию. Сообщение должно содержать 2 фрагмента,"
                "разделенные символом '$'. Попробуйте снова", reply_markup=cancel_kb)
        else:
            await db.create_delivery_method(strings[0], int(strings[1]))
            await data["main_message"].edit_text("Способы доставки:", reply_markup=await get_delivery_kb(
                await db.get_delivery_methods_list()))
            await Settings.DeliveryMethods.set()


@dp.callback_query_handler(choose_delivery_method_cd.filter(), state=Settings.DeliveryMethods)
async def confirm_deletion(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.message.edit_text("Удалить способ доставки?", reply_markup=confirmation_cancel_kb)
    async with state.proxy() as data:
        data["method_id"] = int(callback_data.get("method_id"))
    await Settings.DeliveryMethodDeletionConfirmation.set()


@dp.callback_query_handler(text="yes", state=Settings.DeliveryMethodDeletionConfirmation)
async def delete_method(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        await db.delete_delivery_method(data["method_id"])
    await call.message.edit_text("Способы доставки:", reply_markup=await get_delivery_kb(
        await db.get_delivery_methods_list()))
    await Settings.DeliveryMethods.set()


@dp.callback_query_handler(text="cancel",
                           state=[Settings.DeliveryMethodDeletionConfirmation, Settings.DeliveryMethodInfoRequest])
async def cancel_operation(call: CallbackQuery):
    await call.message.edit_text("Способы доставки:", reply_markup=await get_delivery_kb(
        await db.get_delivery_methods_list()))
    await Settings.DeliveryMethods.set()


@dp.message_handler(text="Способы оплаты", state=[Settings.PaymentMenu, Settings.DeliveryMethods])
async def show_payment_methods(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["main_message"] = await message.answer("Выберите способ оплаты", reply_markup=payment_method_kb)
    await Settings.PaymentMethods.set()


@dp.callback_query_handler(text="spc", state=Settings.PaymentMethods)
async def get_payment_method_info(call: CallbackQuery):
    await call.message.edit_text("Введите информацию об оплате (ее увидят пользователи)")
    await Settings.PaymentMethodInfoRequest.set()


@dp.message_handler(state=Settings.PaymentMethodInfoRequest)
async def set_new_payment_method(message: Message, state: FSMContext):
    utils.misc.config_writer.set_payment_method('SPC', message.text)
    async with state.proxy() as data:
        await data["main_message"].edit_text("Способ оплаты соханен!")

    await Settings.PaymentMenu.set()


@dp.callback_query_handler(state=Settings.PaymentMethods)
async def set_payment_method(call: CallbackQuery, state: FSMContext):
    if call.data == "tlg":
        utils.misc.config_writer.set_payment_method('TLG', 'Оплата онлайн в Telegram')
    elif call.data == "tnf":
        utils.misc.config_writer.set_payment_method('TNF', 'Оплата переводом')
    elif call.data == "csh":
        utils.misc.config_writer.set_payment_method('CSH', 'Оплата наличными курьеру')

    async with state.proxy() as data:
        await data["main_message"].edit_text("Способ оплаты соханен!")

    await Settings.PaymentMenu.set()
