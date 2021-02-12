from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, InputMediaPhoto, InputFile

from data.media_config import IMG_CATALOG_PATH
from filters.is_numeric import IsNumericFilterCallback
from handlers.users.catalog import send_product_info
from keyboards.inline import get_admin_products_kb
from keyboards.inline.admin_catalog import product_info_kb, get_admin_subcategories_kb
from keyboards.inline.general import confirmation_kb
from loader import dp
from states import CatalogEdit
from utils.db_api.api import db_api as db


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

    await call.message.answer("Вы уверены?", reply_markup=confirmation_kb)


@dp.callback_query_handler(text="yes", state=CatalogEdit.ProductDeletionConfirmation)
async def delete_product(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        await db.delete_product(state_data["product_id"])
        catalog_message = state_data["catalog_message"]
    await call.message.delete_reply_markup()
    await call.message.edit_text("Товар удален.")

    await catalog_message.edit_media(InputMediaPhoto(InputFile(IMG_CATALOG_PATH)))
    async with state.proxy() as state_data:
        await catalog_message.edit_reply_markup(
            await get_admin_products_kb(
                await db.get_products_by_page(state_data["category_id"], state_data["page_num"]),
                state_data["page_num"] + 1, state_data["page_total"]))
    await CatalogEdit.ProductsWatching.set()
