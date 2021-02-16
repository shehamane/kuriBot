from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, InputMediaPhoto, InputFile

from data.media_config import IMG_CATALOG_PATH
from filters.is_numeric import IsNumericFilterCallback
from handlers.users.catalog import send_product_info
from keyboards.inline import get_admin_products_kb
from keyboards.inline.admin_catalog import product_info_kb, get_admin_subcategories_kb
from keyboards.inline.general import confirmation_kb, cancel_kb
from loader import dp
from states import CatalogEdit
from utils.db_api.api import db_api as db
from utils.misc.files import download_product_image


@dp.callback_query_handler(IsNumericFilterCallback(), state=CatalogEdit.ProductsWatching)
async def show_product_info(call: CallbackQuery, state: FSMContext):
    await CatalogEdit.ProductWatching.set()
    async with state.proxy() as state_data:
        state_data["product_id"] = int(call.data)
        product = await db.get_product(int(call.data))

        await send_product_info(state_data["catalog_message"], product)
        await state_data["catalog_message"].edit_reply_markup(product_info_kb)


@dp.callback_query_handler(text="back", state=CatalogEdit.ProductWatching)
async def return_to_catalog(call: CallbackQuery, state: FSMContext):
    await call.message.edit_media(InputMediaPhoto(InputFile(IMG_CATALOG_PATH)))
    async with state.proxy() as state_data:
        await call.message.edit_reply_markup(
            await get_admin_products_kb(
                await db.get_products_by_page(state_data["category_id"], state_data["page_num"]),
                state_data["page_num"] + 1, state_data["page_total"]))
    await CatalogEdit.ProductsWatching.set()


@dp.callback_query_handler(text="delete", state=CatalogEdit.ProductWatching)
async def confirm_deletion(call: CallbackQuery, state: FSMContext):
    await CatalogEdit.ProductDeletionConfirmation.set()

    async with state.proxy() as state_data:
        await state_data["catalog_message"].edit_caption("Вы уверены?", reply_markup=confirmation_kb)


@dp.callback_query_handler(text="yes", state=CatalogEdit.ProductDeletionConfirmation)
async def delete_product(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        await db.delete_product(state_data["product_id"])
        catalog_message = state_data["catalog_message"]

    await catalog_message.edit_media(InputMediaPhoto(InputFile(IMG_CATALOG_PATH)))
    async with state.proxy() as state_data:
        await catalog_message.edit_caption("Товар удален",
                                           reply_markup=await get_admin_products_kb(
                                               await db.get_products_by_page(state_data["category_id"],
                                                                             state_data["page_num"]),
                                               state_data["page_num"] + 1, state_data["page_total"]))
    await CatalogEdit.ProductsWatching.set()


@dp.callback_query_handler(text=["change_name", "change_description", "change_price"],
                           state=CatalogEdit.ProductWatching)
async def new_info_request(call: CallbackQuery, state: FSMContext):
    await CatalogEdit.ProductInfoChangeRequest.set()
    async with state.proxy() as state_data:
        state_data["edit_type"] = str(call.data)
        await state_data["catalog_message"].edit_caption("Введите новое значение", reply_markup=cancel_kb)


@dp.message_handler(state=CatalogEdit.ProductInfoChangeRequest)
async def change_info(message: Message, state: FSMContext):
    value = message.text

    async with state.proxy() as state_data:
        if state_data["edit_type"] == "change_name":
            await db.change_product_name(state_data["product_id"], value)
            await show_last_product_info(state=state)
        elif state_data["edit_type"] == "change_description":
            await db.change_product_desctiption(state_data["product_id"], value)
            await show_last_product_info(state=state)
        elif state_data["edit_type"] == "change_price":
            if value.isnumeric():
                await db.change_product_price(state_data["product_id"], int(value))
                await show_last_product_info(state=state)
            else:
                await state_data["catalog_message"].edit_caption("Введите новое значение корректно",
                                                                 reply_markup=cancel_kb)


@dp.callback_query_handler(text="change_image", state=CatalogEdit.ProductWatching)
async def request_image(call: CallbackQuery, state: FSMContext):
    await CatalogEdit.ProductImageChangeRequest.set()
    async with state.proxy() as state_data:
        await state_data["catalog_message"].edit_caption("Отправьте новое изображение", reply_markup=cancel_kb)


@dp.message_handler(content_types=['photo'], state=CatalogEdit.ProductImageChangeRequest)
async def change_image(message: Message, state: FSMContext):
    async with state.proxy() as state_data:
        await download_product_image(state_data["product_id"], message.photo[-1])

    await show_last_product_info(state=state)


@dp.callback_query_handler(text=["cancel", "no"],
                           state=[CatalogEdit.ProductDeletionConfirmation, CatalogEdit.ProductInfoChangeRequest])
async def show_last_product_info(state: FSMContext):
    await CatalogEdit.ProductWatching.set()
    async with state.proxy() as state_data:
        product = await db.get_product(state_data["product_id"])

        await send_product_info(state_data["catalog_message"], product)
        await state_data["catalog_message"].edit_reply_markup(product_info_kb)
