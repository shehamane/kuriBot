from math import ceil

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InputFile

from data.api_config import PRODUCTS_PAGE_VOLUME
from handlers.admin.catalog_navigation import get_category_message
from keyboards.inline.admin_catalog import download_image_kb
from keyboards.inline.general import cancel_kb
from loader import dp
from states import AdminCatalog
from utils.db_api.api import db_api as db
from utils.misc.files import download_product_image


@dp.callback_query_handler(text="new_product",
                           state=[AdminCatalog.Products, AdminCatalog.EmptyCategory])
async def add_new_product(call: CallbackQuery):
    await AdminCatalog.ProductInfoRequest.set()

    text = "Введите информацию о новом продукте по шаблону: " \
           "НАЗВАНИЕ$ОПИСАНИЕ$ЦЕНА (цена указывается только числом, без указания валюты)"

    await call.message.edit_caption(text, reply_markup=cancel_kb)


@dp.message_handler(state=AdminCatalog.ProductInfoRequest)
async def get_info(message: Message, state: FSMContext):
    strings = message.text.split('$')
    async with state.proxy() as data:
        if len(strings) != 3:
            await data["main_message"].edit_caption(
                "Вы неверно ввели информацию. Сообщение должно содержать 3 фрагмента,"
                "разделенные символом '$'. Попробуйте снова", reply_markup=cancel_kb)
        else:
            product_id = await db.create_product(strings[0], strings[1], int(strings[2]), data["category_id"])
            data["product_id"] = product_id

            await data["main_message"].edit_caption("Продукт успешно создан",
                                                    reply_markup=download_image_kb)
            page_total = int(
                ceil(await db.count_products_in_category(data["category_id"]) / PRODUCTS_PAGE_VOLUME))
            if page_total > data["page_total"]:
                data["page_num"] += 1
                data["page_total"] += 1

            await AdminCatalog.ProductImageRequest.set()


@dp.callback_query_handler(text="download_product_image", state=AdminCatalog.ProductImageRequest)
async def download_image(call: CallbackQuery):
    await call.message.edit_caption("Отправьте изображение товара")


@dp.callback_query_handler(text="without_image", state=AdminCatalog.ProductImageRequest)
async def change_state(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        answer = await get_category_message(await db.get_category(data["category_id"]), data)
    await call.message.edit_caption(answer["text"], reply_markup=answer["rm"])
    await AdminCatalog.Products.set()


@dp.message_handler(content_types=['photo'], state=AdminCatalog.ProductImageRequest)
async def get_product_image(message: Message, state: FSMContext):
    async with state.proxy() as data:
        await download_product_image(data["product_id"], message.photo[-1])
        answer = await get_category_message(await db.get_category(data["category_id"]), data)

    await message.answer_photo(InputFile(answer["img_path"]), caption=answer["text"], reply_markup=answer["rm"])
    await AdminCatalog.Products.set()
