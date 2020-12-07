from aiogram.types import Message, CallbackQuery, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from filters.is_positive import IsPositiveFilter
from utils.misc.files import get_product_images

from loader import dp
from utils.db_api.api import db

from keyboards.inline import product_watching_keyboard, return_to_catalog_button, cancel_button
from states import ProductSelection, AddingToCart

from data.api_config import PAGE_VOLUME


async def get_catalog_keyboard(page_num):
    products_list = await db.get_products_list(page_num * PAGE_VOLUME, PAGE_VOLUME)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[

        ]
    )
    for product in products_list:
        text = "id{} - {}"
        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(text=text.format(product["id"], product["name"]),
                                     callback_data=product["id"])
            ]
        )
    keyboard.inline_keyboard.append(
        [
            InlineKeyboardButton(text="<", callback_data="previous"),
            InlineKeyboardButton(text="Отмена", callback_data="cancel"),
            InlineKeyboardButton(text=">", callback_data="next")
        ]
    )
    return keyboard


@dp.message_handler(Text(ignore_case=True, contains=['каталог']), state='*')
async def show_first_page(message: Message, state: FSMContext):
    await state.finish()
    text_help = "Для получения информации о товаре нажмите на него ID.\n" \
                "Чтобы покинуть каталог нажмите или введите \"Отмена\".\n"

    await state.update_data({"page_num": 0})
    await message.answer(text_help, reply_markup=await get_catalog_keyboard(0))
    await ProductSelection.Selection.set()


@dp.callback_query_handler(state=ProductSelection.Selection, text="next")
async def show_next_page(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data["page_num"] < int(await db.count_products() / PAGE_VOLUME):
            data["page_num"] += 1
            await call.message.edit_reply_markup(await get_catalog_keyboard(data["page_num"]))


@dp.callback_query_handler(state=ProductSelection.Selection, text="previous")
async def show_previous_page(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data["page_num"] > 0:
            data["page_num"] -= 1
            await call.message.edit_reply_markup(await get_catalog_keyboard(data["page_num"]))


@dp.callback_query_handler(state=ProductSelection.Selection)
async def show_product(call: CallbackQuery, state: FSMContext):
    product_id = call.data
    await state.update_data({"product_id": product_id})

    product = (await db.get_product(int(product_id)))
    if product:
        await ProductSelection.ProductWatching.set()
        images = await get_product_images(int(product_id))
        if images:
            for path in images:
                await call.message.answer_photo(InputFile(path))

        text = f"{product['name']}\n{product['description']}"
        await call.message.answer(text, reply_markup=product_watching_keyboard)
    else:
        await call.message.answer("Товара с таким ID не существует. (\"Отмена\" для выхода из каталога)")


@dp.callback_query_handler(state=[ProductSelection.ProductWatching, AddingToCart.NumberRequest], text="catalog")
async def show_catalog(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=120)
    await ProductSelection.Selection.set()
    text_help = "Для получения информации о товаре нажмите на него.\n" \
                "Чтобы покинуть каталог нажмите или введите \"Отмена\".\n"

    await state.update_data({"page_num": 0})
    await call.message.answer(text_help, reply_markup=await get_catalog_keyboard(0))
    await ProductSelection.Selection.set()


@dp.callback_query_handler(state=ProductSelection.ProductWatching, text="add_to_cart")
async def add_to_cart(call: CallbackQuery):
    await AddingToCart.NumberRequest.set()
    await call.answer(cache_time=120)
    await call.message.answer("Введите количество товара: ", reply_markup=cancel_button)


@dp.message_handler(IsPositiveFilter(), state=AddingToCart.NumberRequest)
async def get_number(message: Message, state: FSMContext):
    number = int(message.text)
    product_id = int((await state.get_data()).get("product_id"))

    cart_record = await db.get_cart_record_by_product(product_id)
    if not cart_record:
        await db.add_to_cart(product_id, number)
    else:
        await db.change_from_cart(product_id, number + cart_record["number"])
    await message.answer("Товар добавлен в корзину!", reply_markup=return_to_catalog_button)
