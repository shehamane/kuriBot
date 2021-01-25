from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputFile
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from keyboards.inline import get_subcategories_keyboard, get_product_watching_kb
from states import CatalogListing
from keyboards.default import menu
from utils.misc.files import get_product_image_path

from data.media_config import IMG_CATALOG_PATH

from loader import dp
from utils.db_api.api import db_api as db


async def send_product_info(message: Message, product):
    text = f'{product.name}\n' \
           f'{product.description}\n' \
           f'Цена: {product.price} р.'

    img_path = await get_product_image_path(product.id)
    if img_path:
        await message.edit_media(InputMediaPhoto(InputFile(img_path)))

    await message.edit_caption(text)


@dp.message_handler(Text(ignore_case=True, contains=['каталог']), state='*')
async def show_catalog(message: Message, state: FSMContext):
    await state.finish()
    await CatalogListing.CategoryChoosing.set()

    await state.update_data({"category_id": 1})

    text_help = "Вы можете перемещаться по категориям товаров\n" \
                "Для получения информации о товаре нажмите на него.\n" \
                "Чтобы покинуть каталог нажмите или введите \"Отмена\".\n"

    await message.answer_photo(InputFile(IMG_CATALOG_PATH), caption=text_help,
                               reply_markup=await get_subcategories_keyboard(await db.get_subcategories(1)))


@dp.callback_query_handler(state=[CatalogListing.CategoryChoosing, CatalogListing.ProductWatching], text="back")
async def return_to_parent_catalog(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        if state_data["category_id"] == 1:
            await call.message.answer("Вы вернулись в меню.", reply_markup=menu)
            await state.finish()
            return
        else:
            curr_category = await db.get_category(state_data["category_id"])

    await CatalogListing.CategoryChoosing.set()
    await state.update_data({"category_id": curr_category.parent_id})

    await call.message.edit_media(InputMediaPhoto(InputFile(IMG_CATALOG_PATH)))
    await call.message.edit_reply_markup(
        await get_subcategories_keyboard(await db.get_subcategories(curr_category.parent_id)))


@dp.callback_query_handler(state=CatalogListing.CategoryChoosing)
async def show_category(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data)
    await state.update_data({"category_id": category_id})

    category = await db.get_category(category_id)

    if category.is_parent:
        await call.message.edit_reply_markup(await get_subcategories_keyboard(await db.get_subcategories(category_id)))
    else:
        await CatalogListing.ProductWatching.set()
        await state.update_data({"product_number": 0, "product_amount": 1})

        product = await db.get_product_by_page(category_id, 0)
        await state.update_data({"product_id": product.id})

        await send_product_info(call.message, product)
        await call.message.edit_reply_markup(
            await get_product_watching_kb(1, await db.count_category_products(category_id), 1))


#               КНОПКИ ПРОСМОТРА ТОВАРА


@dp.callback_query_handler(state=CatalogListing.ProductWatching, text="next")
async def show_next_product(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        state_data["product_amount"] = 1

        products_number = await db.count_category_products(state_data["category_id"])
        state_data["product_number"] = (state_data["product_number"] + 1) % products_number

        next_product = await db.get_product_by_page(state_data["category_id"],
                                                    state_data["product_number"])

        state_data["product_id"] = next_product.id

        await send_product_info(call.message, next_product)
        await call.message.edit_reply_markup(await get_product_watching_kb(state_data["product_number"] + 1,
                                                                           await db.count_category_products(
                                                                               state_data["category_id"]), 1))


@dp.callback_query_handler(state=CatalogListing.ProductWatching, text="previous")
async def show_previous_product(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        state_data["product_amount"] = 1

        products_number = await db.count_category_products(state_data["category_id"])
        state_data["product_number"] -= 1
        if state_data["product_number"] == -1:
            state_data["product_number"] += products_number

        next_product = await db.get_product_by_page(state_data["category_id"],
                                                    state_data["product_number"])
        state_data["product_id"] = next_product.id

        await send_product_info(call.message, next_product)
        await call.message.edit_reply_markup(await get_product_watching_kb(state_data["product_number"] + 1,
                                                                           products_number, 1))


@dp.callback_query_handler(state=CatalogListing.ProductWatching, text="increase")
async def increase_product_amount(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        state_data["product_amount"] += 1

        products_number = await db.count_category_products(state_data["category_id"])
        await call.message.edit_reply_markup(await get_product_watching_kb(state_data["product_number"] + 1,
                                                                           products_number,
                                                                           state_data["product_amount"]))


@dp.callback_query_handler(state=CatalogListing.ProductWatching, text="decrease")
async def increase_product_amount(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        if state_data["product_amount"] == 1:
            return
        state_data["product_amount"] -= 1

        products_number = await db.count_category_products(state_data["category_id"])
        await call.message.edit_reply_markup(await get_product_watching_kb(state_data["product_number"] + 1,
                                                                           products_number,
                                                                           state_data["product_amount"]))


@dp.callback_query_handler(state=CatalogListing.ProductWatching, text="add_to_cart")
async def add_to_cart(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        cart_record = await db.get_cart_record_by_info(state_data["product_id"])

        if not cart_record:
            await db.add_cart_record(state_data["product_id"], state_data["product_amount"])
        else:
            await db.change_cart_record(state_data["product_id"],
                                        cart_record.amount + state_data["product_amount"])

    products_number = await db.count_category_products(state_data["category_id"])

    await call.message.edit_caption(call.message.caption + "\n Товар добавлен в корзину!",
                                    reply_markup=await get_product_watching_kb(state_data["product_number"] + 1,
                                                                               products_number,
                                                                               state_data["product_amount"]))
