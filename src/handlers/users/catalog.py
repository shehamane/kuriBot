from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.filters import Command, Text
from aiogram.dispatcher import FSMContext

from loader import dp
from utils.db_api.api import db

from keyboards.inline import listing
from keyboards.default import menu
from states.product_selection import ProductSelection

from data.api_config import PAGE_VOLUME


@dp.message_handler(Text(ignore_case=True, contains=['каталог']), state=None)
async def show_first_page(message: Message, state: FSMContext):
    products = await db.get_products_list(0, PAGE_VOLUME)
    text = ""
    if not products:
        text = "Каталог пуст."
    else:
        for number, product in enumerate(products[:10]):
            text += "(" + str(product["id"]) + ") " + product["name"] + "\n"
        await state.update_data({"page_num": 0})
        await ProductSelection.Selection.set()
    await message.answer(text, reply_markup=listing)


@dp.callback_query_handler(state=ProductSelection.Selection, text="next")
async def show_next_page(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=3)
    async with state.proxy() as data:
        if data["page_num"] < int(await db.count_products() / PAGE_VOLUME):
            data["page_num"] += 1

        products = await db.get_products_list(data["page_num"]*PAGE_VOLUME, PAGE_VOLUME)

        text = ""
        for number, product in enumerate(products[:10]):
            text += "(" + str(product["id"]) + ") " + product["name"] + "\n"
        await ProductSelection.Selection.set()
    await call.message.answer(text, reply_markup=listing)


@dp.callback_query_handler(state=ProductSelection.Selection, text="previous")
async def show_previous_page(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=3)
    async with state.proxy() as data:
        if data["page_num"] > 0:
            data["page_num"] -= 1

        products = await db.get_products_list(data["page_num"]*PAGE_VOLUME, PAGE_VOLUME)

        text = ""
        for number, product in enumerate(products[:10]):
            text += "(" + str(product["id"]) + ") " + product["name"] + "\n"
        await ProductSelection.Selection.set()
    await call.message.answer(text, reply_markup=listing)


@dp.message_handler(state=ProductSelection.Selection)
async def show_product(message: Message, state: FSMContext):
    if message.text.isnumeric():
        desc = await db.get_product(int(message.text))
        if desc:
            await message.answer(desc)
        else:
            await message.answer("Неверный ID")
    else:
        await message.answer("Неверный ID")
    await ProductSelection.Selection.set()


@dp.callback_query_handler(state=ProductSelection.Selection, text="cancel")
async def cancel_listing(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=10)
    await call.message.answer("Отмена", reply_markup=menu)
    await state.finish()
