from math import ceil

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, InputFile, CallbackQuery, InputMediaPhoto

from keyboards.default import admin_panel_kb
from keyboards.inline import get_admin_products_kb
from keyboards.inline.admin_catalog import get_admin_subcategories_kb, empty_category_kb
from keyboards.inline.general import cancel_kb
from states import AdminPanel, CatalogEdit

from data.api_config import PRODUCTS_PAGE_VOLUME
from data.media_config import IMG_CATALOG_PATH

from loader import dp
from utils.db_api.api import db_api as db


@dp.message_handler(Text(ignore_case=True, contains=['каталог']),
                    state=[AdminPanel.AdminPanel, CatalogEdit.CategoryChoosing])
async def show_admin_catalog(message: Message, state: FSMContext):
    await state.finish()

    page_total = int(
        ceil(await db.count_products_in_category(1) / PRODUCTS_PAGE_VOLUME))
    if not page_total:
        page_total = 1
    await state.update_data({"category_id": 1, "page_num": 0, "page_total": page_total})

    main = await db.get_category(1)
    if await db.is_empty_category(1) or main.is_parent:
        await CatalogEdit.CategoryChoosing.set()
    else:
        await CatalogEdit.ProductsWatching.set()

    msg = await message.answer_photo(InputFile(IMG_CATALOG_PATH), caption="КАТАЛОГ")
    await send_category_admin_info(msg, state, main)

    await state.update_data({"main_message": msg, "is_photo": False})


@dp.callback_query_handler(text="cancel", state=[CatalogEdit.CategoryChoosing, CatalogEdit.ProductsWatching])
async def return_to_admin_panel(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await AdminPanel.AdminPanel.set()

    await call.message.answer("Вы вернулись в панель администратора", reply_markup=admin_panel_kb)



@dp.callback_query_handler(text="change_image", state=CatalogEdit.CategoryChoosing)
async def change_picture(_, state: FSMContext):
    await CatalogEdit.CatalogImageRequest.set()

    async with state.proxy() as state_data:
        await state_data["main_message"].edit_caption("Пришлите новое изображение", reply_markup=cancel_kb)


@dp.callback_query_handler(text="cancel", state=[CatalogEdit.CatalogImageRequest, CatalogEdit.CategoryNameRequest,
                                                 CatalogEdit.ProductInfoRequest])
async def return_to_category(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        category = await db.get_category(state_data["category_id"])
    await send_category_admin_info(call.message, state, category)
    await CatalogEdit.CategoryChoosing.set()


@dp.message_handler(content_types=['photo'], state=CatalogEdit.CatalogImageRequest)
async def get_catalog_image(message: Message, state: FSMContext):
    await message.photo[-1].download(IMG_CATALOG_PATH)
    async with state.proxy() as state_data:
        if await db.is_empty_category(state_data["category_id"]):
            kb = empty_category_kb
        else:
            kb = await get_admin_subcategories_kb(
                await db.get_subcategories(state_data["category_id"])
            )

        state_data["main_message"] = \
            await message.answer_photo(InputFile(IMG_CATALOG_PATH), caption="Изображение изменено!",
                                       reply_markup=kb)

    await CatalogEdit.CategoryChoosing.set()


@dp.callback_query_handler(text="next", state=CatalogEdit.ProductsWatching)
async def show_next_page(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data["page_num"] + 1 < data["page_total"]:
            data["page_num"] += 1
        category = await db.get_category(data["category_id"])
    await send_category_admin_info(call.message, state, category)


@dp.callback_query_handler(text="previous", state=CatalogEdit.ProductsWatching)
async def show_previous_page(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data["page_num"] > 0:
            data["page_num"] -= 1
        else:
            return
        category = await db.get_category(data["category_id"])
    await send_category_admin_info(call.message, state, category)


async def send_category_admin_info(message: Message, state: FSMContext, category):
    if await db.is_empty_category(category.id):
        await message.edit_reply_markup(empty_category_kb)
    elif category.is_parent:
        await message.edit_reply_markup(await get_admin_subcategories_kb(
            await db.get_subcategories(category.id)
        ))
    else:
        async with state.proxy() as data:
            await message.edit_reply_markup(await get_admin_products_kb(
                await db.get_products_by_page(category.id, data["page_num"], PRODUCTS_PAGE_VOLUME),
                data["page_num"], data["page_total"]
            ))
