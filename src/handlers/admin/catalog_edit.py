from math import ceil

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, InputFile, CallbackQuery, InputMediaPhoto

from data.api_config import PRODUCTS_PAGE_VOLUME
from data.media_config import IMG_CATALOG_PATH
from keyboards.default import admin_panel_kb
from keyboards.inline import get_admin_products_kb
from keyboards.inline.admin_catalog import get_admin_subcategories_kb
from loader import dp
from states import AdminPanel, CatalogEdit
from utils.db_api.api import db_api as db
from utils.misc.files import download_image


@dp.message_handler(Text(ignore_case=True, contains=['каталог']),
                    state=[AdminPanel.AdminPanel, CatalogEdit.CategoryChoosing])
async def show_admin_catalog(message: Message, state: FSMContext):
    await state.finish()
    await CatalogEdit.CategoryChoosing.set()

    await state.update_data({"category_id": 1})

    await message.answer_photo(InputFile(IMG_CATALOG_PATH),
                               reply_markup=await get_admin_subcategories_kb(await db.get_subcategories(1)))


@dp.callback_query_handler(
    state=[CatalogEdit.CategoryChoosing,
           CatalogEdit.ProductsWatching], text="back")
async def return_to_parent_catalog(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        if state_data["category_id"] == 1:
            await call.message.answer("Вы вернулись в панель администратора", reply_markup=admin_panel_kb)
            await AdminPanel.AdminPanel.set()
            return
        else:
            curr_category = await db.get_category(state_data["category_id"])

    await CatalogEdit.CategoryChoosing.set()
    await state.update_data({"category_id": curr_category.parent_id})

    await call.message.edit_media(InputMediaPhoto(InputFile(IMG_CATALOG_PATH)))
    await call.message.edit_reply_markup(
        await get_admin_subcategories_kb(await db.get_subcategories(curr_category.parent_id)))


@dp.callback_query_handler(text="change_image", state=CatalogEdit.CategoryChoosing)
async def change_picture(call: CallbackQuery):
    await CatalogEdit.CatalogImageRequest.set()

    await call.message.answer("Пришлите новое изображение")


@dp.message_handler(content_types=['photo'], state=CatalogEdit.CatalogImageRequest)
async def get_image(message: Message):
    await download_image("catalog.jpg", message.photo[-1])
    await message.answer("Изображение изменено!")

    await CatalogEdit.CategoryChoosing.set()


@dp.callback_query_handler(text="new", state=CatalogEdit.CategoryChoosing)
async def name_request(call: CallbackQuery, state: FSMContext):
    await CatalogEdit.CategoryNameRequest.set()
    await state.update_data({"catalog_message": call.message})
    await call.message.answer("Введите название новой категории")


@dp.message_handler(state=CatalogEdit.CategoryNameRequest)
async def create_new_category(message: Message, state: FSMContext):
    async with state.proxy() as data:
        await db.create_category(message.text, data["category_id"])

        await message.answer(f"Категория {message.text} успешно создана!")

        await CatalogEdit.CategoryChoosing.set()
        await data["catalog_message"].edit_reply_markup(
            await get_admin_subcategories_kb(await db.get_subcategories(data["category_id"])))


@dp.callback_query_handler(state=CatalogEdit.CategoryChoosing)
async def show_category(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data)
    await state.update_data({"category_id": category_id})

    category = await db.get_category(category_id)

    if category.is_parent:
        await call.message.edit_reply_markup(await get_admin_subcategories_kb(await db.get_subcategories(category_id)))
    else:
        await CatalogEdit.ProductsWatching.set()
        await state.update_data({"page_num": 0})
        await state.update_data(
            {"page_total": int(ceil(await db.count_category_products(category_id) / PRODUCTS_PAGE_VOLUME))})

        await call.message.edit_reply_markup(
            await get_admin_products_kb(await db.get_products_by_page(category_id, 0), 1,
                                        (await state.get_data()).get("page_total")))


@dp.callback_query_handler(text="next", state=CatalogEdit.ProductsWatching)
async def show_next_page(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data["page_num"] + 1 < data["page_total"]:
            data["page_num"] += 1
            await call.message.edit_reply_markup(
                await get_admin_products_kb(await db.get_products_by_page(data["category_id"], data["page_num"]),
                                            data["page_num"] + 1, data["page_total"]))


@dp.callback_query_handler(text="previous", state=CatalogEdit.ProductsWatching)
async def show_previous_page(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data["page_num"] > 0:
            data["page_num"] -= 1
            await call.message.edit_reply_markup(
                await get_admin_products_kb(await db.get_products_by_page(data["category_id"], data["page_num"]),
                                            data["page_num"] + 1, data["page_total"]))
