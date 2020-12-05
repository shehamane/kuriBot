from aiogram.types import Message, CallbackQuery, InputFile
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from filters.is_numeric import IsNumericFilter
from utils.misc.files import get_product_images

from loader import dp
from utils.db_api.api import db

from keyboards.inline import listing_keyboard, product_watching_keyboard, return_to_catalog_button, cancel_button
from keyboards.default import menu
from states import ProductSelection, AddingToCart

from data.api_config import PAGE_VOLUME


async def get_products_list_text(products):
    text = ""
    for number, product in enumerate(products[:10]):
        text += "(" + str(product["id"]) + ") " + product["name"] + "\n"
    return text


@dp.message_handler(Text(ignore_case=True, contains=['каталог']), state='*')
async def show_first_page(message: Message, state: FSMContext):
    await state.finish()
    products = await db.get_products_list(0, PAGE_VOLUME)
    if not products:
        await message.answer("Каталог пуст.")
        return
    else:
        text = await get_products_list_text(products)
        await state.update_data({"page_num": 0})

    text_help = "Для получения информации о товаре введите его ID.\n" \
                "Чтобы покинуть каталог нажмите или введите \"Отмена\".\n"
    await message.answer(text_help)
    await message.answer(text, reply_markup=listing_keyboard)
    await ProductSelection.Selection.set()


@dp.callback_query_handler(state=ProductSelection.Selection, text="next")
async def show_next_page(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=0)
    async with state.proxy() as data:
        if data["page_num"] < int(await db.count_products() / PAGE_VOLUME):
            data["page_num"] += 1
        else:
            return

        products = await db.get_products_list(data["page_num"] * PAGE_VOLUME, PAGE_VOLUME)
        text = await get_products_list_text(products)

    await call.message.edit_text(text, reply_markup=listing_keyboard)
    await ProductSelection.Selection.set()


@dp.callback_query_handler(state=ProductSelection.Selection, text="previous")
async def show_previous_page(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=0)
    async with state.proxy() as data:
        if data["page_num"] > 0:
            data["page_num"] -= 1
        else:
            return

        products = await db.get_products_list(data["page_num"] * PAGE_VOLUME, PAGE_VOLUME)
        text = await get_products_list_text(products)

    await call.message.edit_text(text, reply_markup=listing_keyboard)
    await ProductSelection.Selection.set()


@dp.message_handler(IsNumericFilter(), state=ProductSelection.Selection)
async def show_product(message: Message, state: FSMContext):
    product_id = int(message.text)
    await state.update_data({"product_id": product_id})

    product = (await db.get_product(product_id))
    if product:
        images = await get_product_images(product_id)
        if images:
            for path in images:
                await message.answer_photo(InputFile(path))

        text = f"{product['name']}\n{product['description']}"
        await message.answer(text, reply_markup=product_watching_keyboard)
        await ProductSelection.ProductWatching.set()
    else:
        await message.answer("Товара с таким ID не существует. (\"Отмена\" для выхода из каталога)")


@dp.callback_query_handler(state=[ProductSelection.ProductWatching, AddingToCart.NumberRequest], text="catalog")
async def show_catalog(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=120)
    async with state.proxy() as data:
        products = await db.get_products_list(data["page_num"] * PAGE_VOLUME, PAGE_VOLUME)
    if not products:
        await call.message.answer("Каталог пуст.")
        return
    else:
        text = await get_products_list_text(products)
        await state.update_data({"page_num": 0})

    await call.message.answer(text, reply_markup=listing_keyboard)
    await ProductSelection.Selection.set()


@dp.callback_query_handler(state=ProductSelection.ProductWatching, text="add_to_cart")
async def add_to_cart(call: CallbackQuery):
    await AddingToCart.NumberRequest.set()
    await call.answer(cache_time=120)
    await call.message.answer("Введите количество товара: ", reply_markup=cancel_button)


@dp.message_handler(IsNumericFilter(), state=AddingToCart.NumberRequest)
async def get_number(message: Message, state: FSMContext):
    number = int(message.text)
    async with state.proxy() as data:
        await db.add_to_cart(data["product_id"], number)
    await message.answer("Товар добавлен в корзину!", reply_markup=return_to_catalog_button)
