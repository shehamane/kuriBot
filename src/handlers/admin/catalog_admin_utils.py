from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from handlers.admin.catalog_navigation import get_category_message
from keyboards.inline.general import confirmation_kb, cancel_kb
from states import AdminCatalog

from utils.db_api.api import db_api as db
from loader import dp


@dp.callback_query_handler(text="clear", state=AdminCatalog.Categories)
async def confirm_clearing(call: CallbackQuery):
    await AdminCatalog.CatalogClearingConfirmation.set()
    await call.message.edit_caption("Каталог будет очищен. Все данные будут удалены безвозвратно. Продолжить?",
                                    reply_markup=confirmation_kb)


@dp.callback_query_handler(text="yes", state=AdminCatalog.CatalogClearingConfirmation)
async def clear_catalog(call: CallbackQuery, state: FSMContext):
    await db.clear_catalog()
    answer = await get_category_message(await db.get_category(1), state.proxy())
    await call.message.edit_caption(answer["text"], reply_markup=answer["rm"])
    await AdminCatalog.Categories.set()


@dp.callback_query_handler(text="new_category", state=[AdminCatalog.Categories, AdminCatalog.EmptyCategory])
async def name_request(call: CallbackQuery):
    await AdminCatalog.CategoryNameRequest.set()
    await call.message.edit_caption("Введите название новой категории", reply_markup=cancel_kb)


@dp.message_handler(state=AdminCatalog.CategoryNameRequest)
async def create_new_category(message: Message, state: FSMContext):
    async with state.proxy() as data:
        await db.create_category(message.text, data["category_id"])

        answer = await get_category_message(await db.get_category(data["category_id"]), data)
        await data["main_message"].edit_caption(caption=f"Категория {message.text} успешно создана!",
                                                reply_markup=answer["rm"])

    await AdminCatalog.Categories.set()


@dp.callback_query_handler(text="change_name",
                           state=[AdminCatalog.Categories, AdminCatalog.Products, AdminCatalog.EmptyCategory])
async def ask_new_name(call: CallbackQuery):
    await AdminCatalog.CategoryNewNameRequest.set()
    await call.message.edit_caption("Введите новое название категории", reply_markup=cancel_kb)


@dp.message_handler(state=AdminCatalog.CategoryNewNameRequest)
async def change_category_name(message: Message, state: FSMContext):
    async with state.proxy() as data:
        await db.change_category_name(data["category_id"], message.text)
        category = await db.get_category(data["category_id"])
        answer = await get_category_message(category, data)

    await data["main_message"].edit_caption(answer["text"], reply_markup=answer["rm"])

    if await db.is_empty_category(category.id):
        await AdminCatalog.EmptyCategory.set()
    elif category.is_parent:
        await AdminCatalog.Categories.set()
    else:
        await AdminCatalog.Products.set()


@dp.callback_query_handler(text='delete',
                           state=[AdminCatalog.Categories, AdminCatalog.Products, AdminCatalog.EmptyCategory])
async def confirm_deletion(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data["category_id"] == 1:
            return

    await AdminCatalog.CategoryDeletionConfirmation.set()
    await call.message.edit_caption(
        "Все товары и подкатегории из этой категории также будут удалены. Вы уверены?",
        reply_markup=confirmation_kb)


@dp.callback_query_handler(text='yes', state=AdminCatalog.CategoryDeletionConfirmation)
async def delete_category(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        category = await db.get_category(data["category_id"])
        data["category_id"] = category.parent_id
        await db.delete_category(category.id)

    category = await db.get_category(data["category_id"])
    if await db.is_empty_category(category.id):
        await AdminCatalog.EmptyCategory.set()
    else:
        await AdminCatalog.Categories.set()

    answer = await get_category_message(category, data)
    await call.message.edit_caption(answer["text"], reply_markup=answer["rm"])


@dp.callback_query_handler(text="no",
                           state=[AdminCatalog.CategoryDeletionConfirmation, AdminCatalog.CatalogClearingConfirmation])
async def cancel_deletion(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        category = await db.get_category(data["category_id"])

    if await db.is_empty_category(category.id):
        await AdminCatalog.EmptyCategory.set()
    elif category.is_parent:
        await AdminCatalog.Categories.set()
    else:
        await AdminCatalog.Products.set()

    answer = await get_category_message(category, data)
    await call.message.edit_caption(answer["text"], reply_markup=answer["rm"])
