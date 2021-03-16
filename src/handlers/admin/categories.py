from math import ceil

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from data.api_config import PRODUCTS_PAGE_VOLUME
from filters.is_numeric import IsNumericFilterCallback
from handlers.admin.catalog import send_category_admin_info
from keyboards.inline import get_admin_products_kb
from keyboards.inline.admin_catalog import get_admin_subcategories_kb, empty_category_kb
from keyboards.inline.general import confirmation_kb, cancel_kb
from loader import dp
from states import CatalogEdit
from utils.db_api.api import db_api as db


@dp.callback_query_handler(text=["new", "new_category"], state=CatalogEdit.CategoryChoosing)
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
            await call.message.edit_caption("Невозможно удалить главную категорию.",
                                            reply_markup=await get_admin_subcategories_kb(
                                                await db.get_subcategories(state_data["category_id"])))
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


@dp.callback_query_handler(IsNumericFilterCallback(), state=CatalogEdit.CategoryChoosing)
async def show_category(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data)
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
