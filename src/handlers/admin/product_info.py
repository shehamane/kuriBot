from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, InputMediaPhoto, InputFile

from handlers.admin.catalog_navigation import get_category_message
from keyboards.inline.admin_catalog import product_info_kb
from keyboards.inline.general import confirmation_kb, cancel_kb
from states import AdminCatalog
from utils.callback_datas import choose_product_cd
from utils.db_api.api import db_api as db, Product
from utils.misc.files import download_product_image, get_product_image_path

from loader import dp

@dp.callback_query_handler(choose_product_cd.filter(), state=AdminCatalog.Products)
async def show_product_info(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await AdminCatalog.ProductInfo.set()

    async with state.proxy() as data:
        data["product_id"] = int(callback_data.get("product_id"))
    product = await db.get_product(int(callback_data.get("product_id")))
    answer = await get_product_message(product)
    await call.message.edit_media(InputMediaPhoto(InputFile(answer["img_path"])))
    await call.message.edit_caption(answer["text"], reply_markup=answer["rm"])


@dp.callback_query_handler(text="delete", state=AdminCatalog.ProductInfo)
async def confirm_deletion(call: CallbackQuery):
    await AdminCatalog.ProductDeletionConfirmation.set()
    await call.message.edit_caption("Вы уверены?", reply_markup=confirmation_kb)


@dp.callback_query_handler(text="yes", state=AdminCatalog.ProductDeletionConfirmation)
async def delete_product(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        await db.delete_product(data["product_id"])

        category = await db.get_category(data["category_id"])
        answer = await get_category_message(category, data)
    await call.message.edit_media(InputMediaPhoto(InputFile(answer["img_path"])))
    await call.message.edit_caption(answer["text"], reply_markup=answer["rm"])
    await AdminCatalog.Products.set()


@dp.callback_query_handler(text=["change_name", "change_description", "change_price"],
                           state=AdminCatalog.ProductInfo)
async def new_info_request(call: CallbackQuery, state: FSMContext):
    await AdminCatalog.ProductInfoChangeRequest.set()
    async with state.proxy() as data:
        data["edit_type"] = str(call.data)
        data["main_message"] = await call.message.edit_caption("Введите новое значение", reply_markup=cancel_kb)


@dp.message_handler(state=AdminCatalog.ProductInfoChangeRequest)
async def change_info(message: Message, state: FSMContext):
    value = message.text

    async with state.proxy() as data:
        if data["edit_type"] == "change_name":
            await db.change_product_name(data["product_id"], value)
        elif data["edit_type"] == "change_description":
            await db.change_product_description(data["product_id"], value)
        elif data["edit_type"] == "change_price":
            if value.isnumeric():
                await db.change_product_price(data["product_id"], int(value))
            else:
                await data["main_message"].edit_caption("Введите новое значение корректно",
                                                        reply_markup=cancel_kb)
        product = await db.get_product(data["product_id"])
        answer = await get_product_message(product)
        await data["main_message"].edit_caption(answer["text"], reply_markup=answer["rm"])
        await AdminCatalog.ProductInfo.set()


@dp.callback_query_handler(text="change_image", state=AdminCatalog.ProductInfo)
async def request_image(call: CallbackQuery):
    await AdminCatalog.ProductImageChangeRequest.set()

    await call.message.edit_caption("Отправьте новое изображение", reply_markup=cancel_kb)


@dp.message_handler(content_types=['photo'], state=AdminCatalog.ProductImageChangeRequest)
async def change_image(message: Message, state: FSMContext):
    async with state.proxy() as data:
        product = await db.get_product(data["product_id"])

    await download_product_image(product.id, message.photo[-1])
    answer = await get_product_message(product)
    async with state.proxy() as data:
        data["main_message"] = await message.answer_photo(InputFile(answer["img_path"]), caption=answer["text"],
                                                          reply_markup=answer["rm"])
    await AdminCatalog.ProductInfo.set()


@dp.callback_query_handler(text=["no", "cancel"],
                           state=[AdminCatalog.ProductDeletionConfirmation, AdminCatalog.ProductInfoChangeRequest,
                                  AdminCatalog.ProductImageChangeRequest])
async def return_to_product(call: CallbackQuery, state: FSMContext):
    await AdminCatalog.ProductInfo.set()
    async with state.proxy() as data:
        product = await db.get_product(data["product_id"])
    answer = await get_product_message(product)
    await call.message.edit_caption(answer["text"], reply_markup=answer["rm"])


async def get_product_message(product: Product):
    text = f'{product.name}\n' \
           f'{product.description}\n' \
           f'Цена: {product.price} р.'
    message = {"text": text, "rm": product_info_kb, "img_path": await get_product_image_path(product.id)}
    return message
