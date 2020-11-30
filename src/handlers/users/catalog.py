from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from loader import dp
from utils.db_api.api import db

from keyboards.inline import listing
from keyboards.default import menu
from states.product_selection import ProductSelection

from data.api_config import PAGE_VOLUME


async def get_products_list_text(products):
    text = ""
    for number, product in enumerate(products[:10]):
        text += "(" + str(product["id"]) + ") " + product["name"] + "\n"
    return text


@dp.message_handler(Text(ignore_case=True, contains=['каталог']), state=None)
async def show_first_page(message: Message, state: FSMContext):
    products = await db.get_products_list(0, PAGE_VOLUME)
    if not products:
        text = "Каталог пуст."
    else:
        text = await get_products_list_text(products)
        await state.update_data({"page_num": 0})

    text_help = "Для получения информации о товаре введите его ID.\n" \
                "Чтобы покинуть каталог нажмите или введите \"Отмена\".\n"
    await message.answer(text_help)
    await message.answer(text, reply_markup=listing)
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

    await call.message.edit_text(text, reply_markup=listing)
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

    await call.message.edit_text(text, reply_markup=listing)
    await ProductSelection.Selection.set()


@dp.message_handler(Text(equals="отмена", ignore_case=True), state=ProductSelection)
async def cancel_listing(message: Message, state: FSMContext):
    await message.answer("Вы покинули каталог.", reply_markup=menu)
    await state.finish()


@dp.callback_query_handler(state=ProductSelection.Selection, text="cancel")
async def cancel_listing(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=0)
    await call.message.answer("Вы покинули каталог.", reply_markup=menu)
    await state.finish()


@dp.message_handler(state=ProductSelection.Selection)
async def show_product(message: Message):
    if message.text.isnumeric():
        desc = await db.get_product(int(message.text))
        if desc:
            await message.answer(desc)
        else:
            await message.answer("Товара с таким ID не существует. (\"Отмена\" для выхода из каталога)")
    else:
        await message.answer("Неверный ID. (\"Отмена\" для выхода из каталога)")
    await ProductSelection.Selection.set()
