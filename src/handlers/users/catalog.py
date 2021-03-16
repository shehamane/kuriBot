from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputFile
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from filters.is_numeric import IsNumericFilterCallback
from keyboards.default import main_menu_kb
from keyboards.inline.general import back_kb
from utils.misc.files import get_product_image_path
from keyboards.inline import get_subcategories_kb, get_product_watching_kb
from states import CatalogListing

from data.media_config import IMG_CATALOG_PATH, IMG_DEFAULT_PATH

from loader import dp
from utils.db_api.api import db_api as db


@dp.message_handler(Text(ignore_case=True, contains=['каталог']), state='*')
async def show_catalog(message: Message, state: FSMContext):
    await state.finish()
    await CatalogListing.CategoryChoosing.set()
    await state.update_data({"category_id": 1})

    main = await db.get_category(1)
    catalog_message = await message.answer_photo(InputFile(IMG_CATALOG_PATH), caption="КАТАЛОГ")
    await send_category_info(catalog_message, main, state)


@dp.callback_query_handler(state=[CatalogListing.CategoryChoosing, CatalogListing.ProductWatching], text="back")
async def return_to_parent_category(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        if state_data["category_id"] == 1:
            await call.message.answer("Вы покинули каталог.", reply_markup=main_menu_kb)
            await state.finish()
            return
        else:
            curr_category = await db.get_category(state_data["category_id"])

    await state.update_data({"category_id": curr_category.parent_id})
    if not curr_category.is_parent:
        await CatalogListing.CategoryChoosing.set()
        await call.message.edit_media(InputMediaPhoto(InputFile(IMG_CATALOG_PATH)))

    await call.message.edit_reply_markup(
        await get_subcategories_kb(await db.get_subcategories(curr_category.parent_id)))


@dp.callback_query_handler(IsNumericFilterCallback(), state=CatalogListing.CategoryChoosing)
async def show_category(call: CallbackQuery, state: FSMContext):
    category = await db.get_category(int(call.data))
    await state.update_data({"category_id": category.id})
    await send_category_info(call.message, category, state)


# КНОПКИ ПРОСМОТРА ТОВАРА


@dp.callback_query_handler(state=CatalogListing.ProductWatching, text="next")
async def show_next_product(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        state_data["amount"] = 1
        state_data["page_number"] = (state_data["page_number"] + 1) % state_data["page_total"]

        next_product = await db.get_product_by_page(state_data["category_id"],
                                                    state_data["page_number"])
        state_data["product_id"] = next_product.id

        await send_product_info(call.message, next_product)
        await call.message.edit_reply_markup(
            await get_product_watching_kb(state_data["page_number"], state_data["page_total"], 1))


@dp.callback_query_handler(state=CatalogListing.ProductWatching, text="previous")
async def show_previous_product(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        state_data["amount"] = 1
        state_data["page_number"] -= 1
        if state_data["page_number"] == -1:
            state_data["page_number"] += state_data["page_total"]

        previous_product = await db.get_product_by_page(state_data["category_id"],
                                                        state_data["page_number"])
        state_data["product_id"] = previous_product.id

        await send_product_info(call.message, previous_product)
        await call.message.edit_reply_markup(
            await get_product_watching_kb(state_data["page_number"], state_data["page_total"], 1))


@dp.callback_query_handler(state=CatalogListing.ProductWatching, text="increase")
async def increase_amount(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        state_data["amount"] += 1

        await call.message.edit_reply_markup(await get_product_watching_kb(state_data["page_number"],
                                                                           state_data["page_total"],
                                                                           state_data["amount"]))


@dp.callback_query_handler(state=CatalogListing.ProductWatching, text="decrease")
async def decrease_amount(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        if state_data["amount"] == 1:
            return
        state_data["amount"] -= 1

        await call.message.edit_reply_markup(await get_product_watching_kb(state_data["page_number"],
                                                                           state_data["page_total"],
                                                                           state_data["amount"]))


@dp.callback_query_handler(state=CatalogListing.ProductWatching, text="add_to_cart")
async def add_to_cart(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        cart_item = await db.get_cart_item_by_user(state_data["product_id"])

        if not cart_item:
            await db.create_cart_item(state_data["product_id"], state_data["amount"])
        else:
            await db.change_cart_item_amount(cart_item.id,
                                             cart_item.amount + state_data["amount"])

        await call.message.edit_caption(call.message.caption + "\n Товар добавлен в корзину!",
                                        reply_markup=await get_product_watching_kb(state_data["page_number"],
                                                                                   state_data["page_total"],
                                                                                   state_data["amount"]))


async def send_product_info(message: Message, product):
    text = f'{product.name}\n' \
           f'{product.description}\n' \
           f'Цена: {product.price} р.'

    img_path = await get_product_image_path(product.id)
    if img_path:
        await message.edit_media(InputMediaPhoto(InputFile(img_path)))
    else:
        await message.edit_media(InputMediaPhoto(InputFile(IMG_DEFAULT_PATH)))

    await message.edit_caption(text)


async def send_category_info(message: Message, category, state):
    if category.is_parent:
        await message.edit_reply_markup(await get_subcategories_kb(await db.get_subcategories(category.id)))
    else:
        await CatalogListing.ProductWatching.set()

        page_total = await db.count_products_in_category(category.id)

        if not page_total:
            await message.edit_caption("Категория пуста.", reply_markup=back_kb)
            return
        product = await db.get_product_by_page(category.id, 0)

        await state.update_data({"product_id": product.id, "page_number": 0,
                                 "amount": 1, "page_total": page_total})

        await send_product_info(message, product)
        await message.edit_reply_markup(
            await get_product_watching_kb(0, page_total, 1))
