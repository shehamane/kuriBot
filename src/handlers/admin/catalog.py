from math import ceil

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, InputFile, CallbackQuery, InputMediaPhoto

from data.api_config import PRODUCTS_PAGE_VOLUME
from data.media_config import IMG_CATALOG_PATH
from keyboards.default import admin_panel_kb
from keyboards.inline import get_admin_products_kb
from keyboards.inline.admin_catalog import get_admin_subcategories_kb, empty_category_kb
from keyboards.inline.general import cancel_kb
from loader import dp
from states import AdminPanel, CatalogEdit
from utils.db_api.api import db_api as db
from utils.misc.files import download_image


@dp.message_handler(Text(ignore_case=True, contains=['каталог']),
                    state=[AdminPanel.AdminPanel, CatalogEdit.CategoryChoosing])
async def show_admin_catalog(message: Message, state: FSMContext):
    await state.finish()

    await state.update_data({"category_id": 1})
    async with state.proxy() as state_data:
        if not ((await db.count_category_products(1)) or (await db.count_subcategories(1))):
            await CatalogEdit.CategoryChoosing.set()
            state_data["catalog_message"] = await message.answer_photo(InputFile(IMG_CATALOG_PATH),
                                                                       reply_markup=empty_category_kb)
            state_data["page_num"] = 0
            state_data["page_total"] = 0
        else:
            await CatalogEdit.CategoryChoosing.set()
            main = await db.get_category(1)
            if main.is_parent:
                state_data["catalog_message"] = await message.answer_photo(InputFile(IMG_CATALOG_PATH),
                                                                           reply_markup=await get_admin_subcategories_kb(
                                                                               await db.get_subcategories(1)))
            else:
                await CatalogEdit.ProductsWatching.set()
                state_data["page_num"] = 0
                state_data["page_total"] = int(
                    ceil(await db.count_category_products(state_data["category_id"]) / PRODUCTS_PAGE_VOLUME))
                state_data["catalog_message"] = await message.answer_photo(InputFile(IMG_CATALOG_PATH),
                                                                           reply_markup=await get_admin_products_kb(
                                                                               await db.get_category_products(1), 1,
                                                                               state_data["page_total"]))


@dp.callback_query_handler(text="cancel", state=[CatalogEdit.CategoryChoosing, CatalogEdit.ProductsWatching])
async def return_to_admin_panel(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await AdminPanel.AdminPanel.set()

    await call.message.answer("Вы вернулись в панель администратора", reply_markup=admin_panel_kb)


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
async def change_picture(call: CallbackQuery, state: FSMContext):
    await CatalogEdit.CatalogImageRequest.set()

    async with state.proxy() as state_data:
        await state_data["catalog_message"].edit_caption("Пришлите новое изображение", reply_markup=cancel_kb)


@dp.callback_query_handler(text="cancel", state=[CatalogEdit.CatalogImageRequest, CatalogEdit.CategoryNameRequest])
async def return_to_category(call: CallbackQuery, state: FSMContext):
    await CatalogEdit.CategoryChoosing.set()

    async with state.proxy() as state_data:
        await state_data["catalog_message"].edit_caption("", reply_markup=await get_admin_subcategories_kb(
            await db.get_subcategories(state_data["category_id"])))


@dp.message_handler(content_types=['photo'], state=CatalogEdit.CatalogImageRequest)
async def get_catalog_image(message: Message, state: FSMContext):
    await download_image("catalog.jpg", message.photo[-1])
    async with state.proxy() as state_data:
        await state_data["catalog_message"].edit_media(InputMediaPhoto(InputFile(IMG_CATALOG_PATH)))
        if not state_data["page_total"]:
            await state_data["catalog_message"].edit_caption("Изображение изменено!",
                                                             reply_markup=empty_category_kb)
        else:
            await state_data["catalog_message"].edit_caption("Изображение изменено!",
                                                             reply_markup=await get_admin_subcategories_kb(
                                                                 await db.get_subcategories(state_data["category_id"])))
    await CatalogEdit.CategoryChoosing.set()


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
