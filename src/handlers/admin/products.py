from aiogram.dispatcher import FSMContext
from aiogram.types import Message, InputFile, CallbackQuery

from data.media_config import IMG_CATALOG_PATH
from keyboards.inline import get_admin_products_kb
from keyboards.inline.admin_catalog import download_image_kb
from keyboards.inline.general import cancel_kb
from loader import dp
from states import CatalogEdit
from utils.db_api.api import db_api as db
from utils.misc.files import download_product_image


@dp.callback_query_handler(text="new", state=CatalogEdit.ProductsWatching)
async def add_new_product(call: CallbackQuery):
    await CatalogEdit.ProductInfoRequest.set()
    await call.message.answer("Введите информацию о новом продукте по шаблону:\n"
                              "НАЗВАНИЕ\n"
                              "ОПИСАНИЕ\n"
                              "ЦЕНА\n", reply_markup=cancel_kb)


@dp.message_handler(state=CatalogEdit.ProductInfoRequest)
async def confirm_addition(message: Message, state: FSMContext):
    strings = message.text.split('\n')
    if len(strings) != 3:
        await message.answer("Вы неверно ввели информацию. Сообщение должно содержать 3 строки, как указано в шаблоне")
    else:
        async with state.proxy() as state_data:
            product_id = await db.create_product(strings[0], strings[1], int(strings[2]), state_data["category_id"])
            await message.answer("Продукт успешно создан!", reply_markup=download_image_kb)

            state_data["product_id"] = product_id
            await CatalogEdit.ProductImageWaiting.set()


@dp.callback_query_handler(text="download_product_image", state=CatalogEdit.ProductImageWaiting)
async def download_image(call: CallbackQuery, state: FSMContext):
    await CatalogEdit.ProductImageRequest.set()

    await call.message.answer("Отправьте изображение товара")


@dp.callback_query_handler(text="without_image", state=CatalogEdit.ProductImageWaiting)
async def change_state(call: CallbackQuery, state: FSMContext):
    await call.message.delete_reply_markup()
    async with state.proxy() as state_data:
        await call.message.answer_photo(InputFile(IMG_CATALOG_PATH), caption="Изображение добавлено!",
                                        reply_markup=await get_admin_products_kb(
                                            await db.get_products_by_page(state_data["category_id"], 0), 1,
                                            state_data["page_total"]))

        await CatalogEdit.ProductsWatching.set()


@dp.message_handler(content_types=['photo'], state=CatalogEdit.ProductImageRequest)
async def get_product_image(message: Message, state: FSMContext):
    async with state.proxy() as state_data:
        await download_product_image(state_data["product_id"], message.photo[-1])
        await message.answer_photo(InputFile(IMG_CATALOG_PATH), caption="Изображение добавлено!",
                                   reply_markup=await get_admin_products_kb(
                                       await db.get_products_by_page(state_data["category_id"], 0), 1,
                                       state_data["page_total"]))

        await CatalogEdit.ProductsWatching.set()
