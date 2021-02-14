from math import ceil

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from data.api_config import PRODUCTS_PAGE_VOLUME
from keyboards.inline import get_admin_products_kb
from keyboards.inline.admin_catalog import get_admin_subcategories_kb, empty_category_kb
from keyboards.inline.general import confirmation_kb, cancel_kb
from loader import dp
from states import CatalogEdit
from utils.db_api.api import db_api as db


@dp.callback_query_handler(text=["new", "new_category"], state=CatalogEdit.CategoryChoosing)
async def name_request(call: CallbackQuery, state: FSMContext):
    await CatalogEdit.CategoryNameRequest.set()

    async with state.proxy() as state_data:
        await state_data["catalog_message"].edit_caption("Введите название новой категории", reply_markup=cancel_kb)


@dp.message_handler(state=CatalogEdit.CategoryNameRequest)
async def create_new_category(message: Message, state: FSMContext):
    async with state.proxy() as state_data:
        await db.create_category(message.text, state_data["category_id"])
        await state_data["catalog_message"].edit_caption(caption=f"Категория {message.text} успешно создана!",
                                                         reply_markup=await get_admin_subcategories_kb(
                                                             await db.get_subcategories(state_data["category_id"])))

    await CatalogEdit.CategoryChoosing.set()


@dp.callback_query_handler(text='delete', state=[CatalogEdit.CategoryChoosing, CatalogEdit.ProductsWatching])
async def confirm_deletion(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        if state_data["category_id"] == 1:
            await state_data["catalog_message"].edit_caption("Невозможно удалить главную категорию.",
                                                             reply_markup=await get_admin_subcategories_kb(
                                                                 await db.get_subcategories(state_data["category_id"])))
            return

        await CatalogEdit.CategoryDeletionConfirmation.set()
        await state_data["catalog_message"].edit_caption(
            "Все товары и подкатегории из этой категории также будут удалены. Вы уверены?",
            reply_markup=confirmation_kb)


@dp.callback_query_handler(text='yes', state=CatalogEdit.CategoryDeletionConfirmation)
async def delete_category(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        category = await db.get_category(state_data["category_id"])
        state_data["category_id"] = category.parent_id
        await db.delete_category(category.id)

        if not (await db.count_subcategories(category.parent_id)):
            await state_data["catalog_message"].edit_caption(caption="Категория успешно удалена!",
                                                             reply_markup=empty_category_kb)
        else:
            await state_data["catalog_message"].edit_caption(reply_markup=await get_admin_subcategories_kb(
                await db.get_subcategories(category.parent_id)),
                                                             caption="Категория успешно удалена!")

        await CatalogEdit.CategoryChoosing.set()


@dp.callback_query_handler(text="no", state=CatalogEdit.CategoryDeletionConfirmation)
async def cancel_deletion(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        category = await db.get_category(state_data["category_id"])
        if not ((await db.count_category_products(category.id)) or (await db.count_subcategories(category.id))):
            await state_data["catalog_message"].edit_reply_markup(empty_category_kb)
        else:
            if category.is_parent:
                await state_data["catalog_message"].edit_reply_markup(await get_admin_subcategories_kb(
                    await db.get_subcategories(state_data["category_id"])))
            else:
                await state_data["catalog_message"].edit_reply_markup(await get_admin_products_kb(
                    await db.get_category_products(state_data["category_id"]), state_data["page_num"] + 1,
                    state_data["page_total"]))
    await CatalogEdit.CategoryChoosing.set()


@dp.callback_query_handler(state=CatalogEdit.CategoryChoosing)
async def show_category(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data)
    await state.update_data({"category_id": category_id})

    category = await db.get_category(category_id)

    if not ((await db.count_category_products(category_id)) or (await db.count_subcategories(category_id))):
        await call.message.edit_reply_markup(empty_category_kb)
    else:
        if category.is_parent:
            await call.message.edit_reply_markup(
                await get_admin_subcategories_kb(await db.get_subcategories(category_id)))
        else:
            await CatalogEdit.ProductsWatching.set()
            await state.update_data({"page_num": 0})
            await state.update_data(
                {"page_total": int(ceil(await db.count_category_products(category_id) / PRODUCTS_PAGE_VOLUME))})

            await call.message.edit_reply_markup(
                await get_admin_products_kb(await db.get_products_by_page(category_id, 0), 1,
                                            (await state.get_data()).get("page_total")))
