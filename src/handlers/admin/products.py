from math import ceil

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, InputFile, CallbackQuery

from data.api_config import PRODUCTS_PAGE_VOLUME
from data.media_config import IMG_CATALOG_PATH
from keyboards.inline import get_admin_products_kb
from keyboards.inline.admin_catalog import download_image_kb
from keyboards.inline.general import cancel_kb
from loader import dp
from states import CatalogEdit
from utils.db_api.api import db_api as db
from utils.misc.files import download_product_image


@dp.callback_query_handler(text=["new", "new_product"],
                           state=[CatalogEdit.ProductsWatching, CatalogEdit.CategoryChoosing])
async def add_new_product(call: CallbackQuery, state: FSMContext):
    await CatalogEdit.ProductInfoRequest.set()

    text = "Введите информацию о новом продукте по шаблону:\n"
    "НАЗВАНИЕ\n"
    "ОПИСАНИЕ\n"
    "ЦЕНА\n"

    async with state.proxy() as state_data:
        await state_data["catalog_message"].edit_caption(text, reply_markup=cancel_kb)


@dp.message_handler(state=CatalogEdit.ProductInfoRequest)
async def get_info(message: Message, state: FSMContext):
    strings = message.text.split('\n')
    async with state.proxy() as state_data:
        if len(strings) != 3:
            await state_data["catalog_message"].edit_caption(
                "Вы неверно ввели информацию. Сообщение должно содержать 3 строки,"
                " как указано в шаблоне. Попробуйте снова", reply_markup=cancel_kb)
        else:
            product_id = await db.create_product(strings[0], strings[1], int(strings[2]), state_data["category_id"])
            await state_data["catalog_message"].edit_caption("Продукт успешно создан",
                                                             reply_markup=download_image_kb)
            state_data["page_total"] = int(
                ceil(await db.count_category_products(state_data["category_id"]) / PRODUCTS_PAGE_VOLUME))

            state_data["product_id"] = product_id
            await CatalogEdit.ProductImageWaiting.set()


@dp.callback_query_handler(text="download_product_image", state=CatalogEdit.ProductImageWaiting)
async def download_image(call: CallbackQuery, state: FSMContext):
    await CatalogEdit.ProductImageRequest.set()

    async with state.proxy() as state_data:
        await state_data["catalog_message"].edit_caption("Отправьте изображение товара")


@dp.callback_query_handler(text="without_image", state=CatalogEdit.ProductImageWaiting)
async def change_state(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        await call.message.edit_reply_markup(await get_admin_products_kb(
            await db.get_products_by_page(state_data["category_id"], state_data["page_num"]),
            state_data["page_num"] + 1,
            state_data["page_total"]))

        await CatalogEdit.ProductsWatching.set()


@dp.message_handler(content_types=['photo'], state=CatalogEdit.ProductImageRequest)
async def get_product_image(message: Message, state: FSMContext):
    async with state.proxy() as state_data:
        await download_product_image(state_data["product_id"], message.photo[-1])
        await state_data["catalog_message"].edit_caption(caption="Изображение добавлено!",
                                                         reply_markup=await get_admin_products_kb(
                                                             await db.get_products_by_page(
                                                                 state_data["category_id"],
                                                                 0), 1,
                                                             state_data["page_total"]))

        await CatalogEdit.ProductsWatching.set()
