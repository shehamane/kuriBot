from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, InputMediaPhoto, InputFile

from data.media_config import IMG_CATALOG_PATH
from filters.is_numeric import IsNumericFilterCallback
from handlers.admin.catalog import send_category_admin_info
from handlers.users.catalog import send_product_info
from keyboards.inline.admin_catalog import product_info_kb
from keyboards.inline.general import confirmation_kb, cancel_kb
from loader import dp
from states import CatalogEdit
from utils.db_api.api import db_api as db
from utils.misc.files import download_product_image, get_product_image_path


@dp.callback_query_handler(IsNumericFilterCallback(), state=CatalogEdit.ProductsWatching)
async def show_product_info(call: CallbackQuery, state: FSMContext):
    await CatalogEdit.ProductWatching.set()

    async with state.proxy() as state_data:
        state_data["product_id"] = int(call.data)
        product = await db.get_product(int(call.data))

        await send_product_info(state_data["main_message"], product)
        await call.message.edit_reply_markup(product_info_kb)


@dp.callback_query_handler(text="back", state=CatalogEdit.ProductWatching)
async def return_to_catalog(call: CallbackQuery, state: FSMContext):
    await call.message.edit_media(InputMediaPhoto(InputFile(IMG_CATALOG_PATH)))
    async with state.proxy() as state_data:
        category = await db.get_category(state_data["category_id"])
    await send_category_admin_info(call.message, state, category)
    await CatalogEdit.ProductsWatching.set()


@dp.callback_query_handler(text="delete", state=CatalogEdit.ProductWatching)
async def confirm_deletion(call: CallbackQuery):
    await CatalogEdit.ProductDeletionConfirmation.set()

    await call.message.edit_caption("Вы уверены?", reply_markup=confirmation_kb)


@dp.callback_query_handler(text="yes", state=CatalogEdit.ProductDeletionConfirmation)
async def delete_product(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        await db.delete_product(state_data["product_id"])

    category = await db.get_category(state_data["category_id"])

    await call.message.edit_media(InputMediaPhoto(InputFile(IMG_CATALOG_PATH)))
    await send_category_admin_info(call.message, state, category)
    await CatalogEdit.ProductsWatching.set()


@dp.callback_query_handler(text=["change_name", "change_description", "change_price"],
                           state=CatalogEdit.ProductWatching)
async def new_info_request(call: CallbackQuery, state: FSMContext):
    await CatalogEdit.ProductInfoChangeRequest.set()
    async with state.proxy() as state_data:
        state_data["edit_type"] = str(call.data)
        state_data["main_message"] = await call.message.edit_caption("Введите новое значение", reply_markup=cancel_kb)


@dp.message_handler(state=CatalogEdit.ProductInfoChangeRequest)
async def change_info(message: Message, state: FSMContext):
    value = message.text

    async with state.proxy() as state_data:
        if state_data["edit_type"] == "change_name":
            await db.change_product_name(state_data["product_id"], value)
            await show_current_product(state_data["main_message"], state)
        elif state_data["edit_type"] == "change_description":
            await db.change_product_description(state_data["product_id"], value)
            await show_current_product(state_data["main_message"], state)
        elif state_data["edit_type"] == "change_price":
            if value.isnumeric():
                await db.change_product_price(state_data["product_id"], int(value))
                await show_current_product(state_data["main_message"], state)
            else:
                await state_data["main_message"].edit_caption("Введите новое значение корректно",
                                                              reply_markup=cancel_kb)


@dp.callback_query_handler(text="change_image", state=CatalogEdit.ProductWatching)
async def request_image(call: CallbackQuery):
    await CatalogEdit.ProductImageChangeRequest.set()

    await call.message.edit_caption("Отправьте новое изображение", reply_markup=cancel_kb)


@dp.message_handler(content_types=['photo'], state=CatalogEdit.ProductImageChangeRequest)
async def change_image(message: Message, state: FSMContext):
    async with state.proxy() as state_data:
        product = await db.get_product(state_data["product_id"])

    await download_product_image(product.id, message.photo[-1])
    img_path = await get_product_image_path(product.id)
    text = f'{product.name}\n' \
           f'{product.description}\n' \
           f'Цена: {product.price} р.'

    async with state.proxy() as state_data:
        state_data["main_message"] = await message.answer_photo(InputFile(img_path), caption=text,
                                                                reply_markup=product_info_kb)
    await CatalogEdit.ProductWatching.set()


@dp.callback_query_handler(text=["no", "cancel"],
                           state=[CatalogEdit.ProductDeletionConfirmation, CatalogEdit.ProductInfoChangeRequest,
                                  CatalogEdit.ProductImageChangeRequest])
async def return_to_product(call: CallbackQuery, state: FSMContext):
    await show_current_product(call.message, state)


async def show_current_product(message: Message, state: FSMContext):
    await CatalogEdit.ProductWatching.set()
    async with state.proxy() as state_data:
        product = await db.get_product(state_data["product_id"])

        text = f'{product.name}\n' \
               f'{product.description}\n' \
               f'Цена: {product.price} р.'

        await message.edit_caption(text, reply_markup=product_info_kb)
