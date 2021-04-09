from math import ceil

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputFile

from data.media_config import IMG_CATALOG_PATH
from handlers.admin.catalog import send_category_admin_info

from keyboards.default import admin_panel_kb
from keyboards.inline import get_admin_products_kb
from keyboards.inline.admin_catalog import get_admin_subcategories_kb, empty_category_kb
from keyboards.inline.general import confirmation_kb, cancel_kb
from states import CatalogEdit, AdminPanel

from data.api_config import PRODUCTS_PAGE_VOLUME
from utils.callback_datas import choose_category_cd

from utils.db_api.api import db_api as db
from loader import dp


@dp.callback_query_handler(text=["new", "new_category"],
                           state=[CatalogEdit.CategoryChoosing, CatalogEdit.ProductsWatching])
async def name_request(call: CallbackQuery):
    await CatalogEdit.CategoryNameRequest.set()
    await call.message.edit_caption("Введите название новой категории", reply_markup=cancel_kb)


@dp.message_handler(state=CatalogEdit.CategoryNameRequest)
async def create_new_category(message: Message, state: FSMContext):
    async with state.proxy() as state_data:
        await db.create_category(message.text, state_data["category_id"])
        await state_data["main_message"].edit_caption(caption=f"Категория {message.text} успешно создана!",
                                                      reply_markup=await get_admin_subcategories_kb(
                                                          await db.get_subcategories(state_data["category_id"])))

    await CatalogEdit.CategoryChoosing.set()


@dp.callback_query_handler(text='delete', state=[CatalogEdit.CategoryChoosing, CatalogEdit.ProductsWatching])
async def confirm_deletion(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        if state_data["category_id"] == 1:
            if await db.is_empty_category(1):
                kb = empty_category_kb
            else:
                main = await db.get_category(1)
                if main.is_parent:
                    kb = await get_admin_subcategories_kb(
                        await db.get_subcategories(1))
                else:
                    kb = await get_admin_products_kb(
                        await db.get_products_by_page(1,
                                                      state_data["page_num"],
                                                      PRODUCTS_PAGE_VOLUME),
                        state_data["page_num"], state_data["page_total"])
            await call.message.edit_caption("Невозможно удалить главную категорию.",
                                            reply_markup=kb)
            return

    await CatalogEdit.CategoryDeletionConfirmation.set()
    await call.message.edit_caption(
        "Все товары и подкатегории из этой категории также будут удалены. Вы уверены?",
        reply_markup=confirmation_kb)


@dp.callback_query_handler(text='yes', state=CatalogEdit.CategoryDeletionConfirmation)
async def delete_category(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        category = await db.get_category(state_data["category_id"])
        state_data["category_id"] = category.parent_id
        await db.delete_category(category.id)

    category = await db.get_category(state_data["category_id"])
    await send_category_admin_info(call.message, state, category)
    await CatalogEdit.CategoryChoosing.set()


@dp.callback_query_handler(text="no", state=CatalogEdit.CategoryDeletionConfirmation)
async def cancel_deletion(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        category = await db.get_category(state_data["category_id"])

    if await db.is_empty_category(category.id) or category.is_parent:
        await CatalogEdit.CategoryChoosing.set()
    else:
        await CatalogEdit.ProductsWatching.set()

    await send_category_admin_info(call.message, state, category)


@dp.callback_query_handler(choose_category_cd.filter(), state=CatalogEdit.CategoryChoosing)
async def show_category(call: CallbackQuery, callback_data: dict, state: FSMContext):
    category_id = int(callback_data.get("category_id"))
    page_total = int(
        ceil(await db.count_products_in_category(category_id) / PRODUCTS_PAGE_VOLUME))
    if not page_total:
        page_total = 1
    await state.update_data({"category_id": category_id, "page_num": 0, "page_total": page_total})

    category = await db.get_category(category_id)
    if await db.is_empty_category(category_id) or category.is_parent:
        await CatalogEdit.CategoryChoosing.set()
    else:
        await CatalogEdit.ProductsWatching.set()

    await send_category_admin_info(call.message, state, category)


@dp.callback_query_handler(
    state=[CatalogEdit.CategoryChoosing,
           CatalogEdit.ProductsWatching], text="back")
async def return_to_parent_category(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        if state_data["category_id"] == 1:
            await call.message.answer("Вы вернулись в панель администратора", reply_markup=admin_panel_kb)
            await AdminPanel.AdminPanel.set()
            return
        else:
            curr_category = await db.get_category(state_data["category_id"])

    await CatalogEdit.CategoryChoosing.set()
    await state.update_data({"category_id": curr_category.parent_id})

    if state == CatalogEdit.ProductsWatching:
        await call.message.edit_media(InputMediaPhoto(InputFile(IMG_CATALOG_PATH)))
    await call.message.edit_reply_markup(
        await get_admin_subcategories_kb(await db.get_subcategories(curr_category.parent_id)))
