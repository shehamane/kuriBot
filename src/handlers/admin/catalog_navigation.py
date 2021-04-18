from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, InputFile, CallbackQuery, InputMediaPhoto

from keyboards.inline import get_admin_products_kb
from keyboards.inline.admin_catalog import get_admin_subcategories_kb, empty_category_kb
from states import AdminPanel, AdminCatalog, UserInfo

from data.api_config import PRODUCTS_PAGE_VOLUME
from data.media_config import IMG_CATALOG_PATH

from loader import dp
from utils.callback_datas import choose_category_cd
from utils.db_api.api import db_api as db, Category


@dp.message_handler(Text(ignore_case=True, contains=['каталог']),
                    state=[AdminPanel.AdminPanel, AdminCatalog.Categories, UserInfo.OrderInfo,
                           UserInfo.UsersList, UserInfo.OrdersList])
async def show_main_category(message: Message, state: FSMContext):
    await state.finish()
    await state.update_data({"category_id": 1})

    main = await db.get_category(1)
    if await db.is_empty_category(1):
        await AdminCatalog.EmptyCategory.set()
        await state.update_data({"page_num": -1,
                                 "page_total": 0})
    elif main.is_parent:
        await AdminCatalog.Categories.set()
    else:
        await AdminCatalog.Products.set()
        await state.update_data({"page_num": 0,
                                 "page_total": await db.count_pages_in_category(main.id, PRODUCTS_PAGE_VOLUME)})

    async with state.proxy() as data:
        answer = await get_category_message(main, data)
        data["main_message"] = await message.answer_photo(InputFile(answer["img_path"]), caption=answer["text"],
                                                          reply_markup=answer["rm"])


@dp.callback_query_handler(choose_category_cd.filter(), state=AdminCatalog.Categories)
async def show_category(call: CallbackQuery, callback_data: dict, state: FSMContext):
    category_id = int(callback_data.get("category_id"))
    await state.update_data({"category_id": category_id})

    category = await db.get_category(category_id)
    if await db.is_empty_category(category.id):
        await AdminCatalog.EmptyCategory.set()
        await state.update_data({"page_num": -1,
                                 "page_total": 0})
    elif category.is_parent:
        await AdminCatalog.Categories.set()
    else:
        await AdminCatalog.Products.set()
        await state.update_data({"page_num": 0,
                                 "page_total": await db.count_pages_in_category(category.id, PRODUCTS_PAGE_VOLUME)})

    async with state.proxy() as data:
        answer = await get_category_message(category, data)
    await call.message.edit_caption(caption=answer["text"], reply_markup=answer["rm"])


@dp.callback_query_handler(
    state=[AdminCatalog.Categories, AdminCatalog.Products, AdminCatalog.ProductInfo, AdminCatalog.EmptyCategory],
    text="back")
async def return_to_parent_category(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data["category_id"] == 1:
            return
        curr_category = await db.get_category(data["category_id"])
    if await state.get_state() != "AdminCatalog:ProductInfo":
        curr_category = await db.get_category(curr_category.parent_id)

    await state.update_data({"category_id": curr_category.id})

    async with state.proxy() as data:
        answer = await get_category_message(curr_category, data)
    if await state.get_state() == "AdminCatalog:ProductInfo":
        await AdminCatalog.Products.set()
        await call.message.edit_media(InputMediaPhoto(InputFile(answer["img_path"])))
    else:
        await AdminCatalog.Categories.set()
    await call.message.edit_caption(answer["text"], reply_markup=answer["rm"])



@dp.callback_query_handler(text="cancel", state=[AdminCatalog.CatalogImageRequest, AdminCatalog.CategoryNameRequest,
                                                 AdminCatalog.ProductInfoRequest])
async def return_to_category(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        category = await db.get_category(data["category_id"])

    async with state.proxy() as data:
        answer = await get_category_message(category, data)
    await call.message.edit_caption(caption=answer["text"], reply_markup=answer["rm"])
    await AdminCatalog.Categories.set()


@dp.callback_query_handler(text="next", state=AdminCatalog.Products)
async def show_next_page(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data["page_num"] + 1 < data["page_total"]:
            data["page_num"] += 1
        category = await db.get_category(data["category_id"])
    async with state.proxy() as data:
        answer = await get_category_message(category, data)
    await call.message.edit_caption(caption=answer["text"], reply_markup=answer["rm"])


@dp.callback_query_handler(text="previous", state=AdminCatalog.Products)
async def show_previous_page(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data["page_num"] > 0:
            data["page_num"] -= 1
        else:
            return
        category = await db.get_category(data["category_id"])
    async with state.proxy() as data:
        answer = await get_category_message(category, data)
    await call.message.edit_caption(caption=answer["text"], reply_markup=answer["rm"])


async def get_category_message(category: Category, data):
    message = {"text": category.name, "img_path": IMG_CATALOG_PATH}

    if await db.is_empty_category(category.id):
        message["rm"] = empty_category_kb
    elif category.is_parent:
        message["rm"] = await get_admin_subcategories_kb(await db.get_subcategories(category.id), category.id == 1)
    else:
        message["rm"] = await get_admin_products_kb(
            await db.get_products_by_page(category.id, data["page_num"], PRODUCTS_PAGE_VOLUME),
            data["page_num"], data["page_total"])
    return message
