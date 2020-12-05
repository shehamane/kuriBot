from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputFile

from keyboards.inline import product_watching_keyboard, cart_record_watching
from utils.misc.files import get_product_images
from states import CartListing

from loader import dp
from utils.db_api.api import db

from data.api_config import PAGE_VOLUME


async def get_cart_keyboard(page_num):
    cart_list = await db.get_cart_list(page_num * PAGE_VOLUME, PAGE_VOLUME)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[

        ]
    )
    for cart_record in cart_list:
        product = await db.get_product(cart_record["product_id"])
        text = "{} - {} шт."
        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(text=text.format(product["name"], cart_record["number"]),
                                     callback_data=cart_record["id"])
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


@dp.message_handler(Text(contains=['корзина'], ignore_case=True), state='*')
async def show_cart(message: Message, state: FSMContext):
    await state.finish()
    await CartListing.CartWatching.set()
    await state.update_data({"page_num": 0})
    await message.answer("Ваша корзина: ", reply_markup=await get_cart_keyboard(0))


@dp.callback_query_handler(text="next", state=CartListing.CartWatching)
async def show_next_page(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data["page_num"] < int(await db.count_cart() / (PAGE_VOLUME + 1)):
            data["page_num"] += 1
            await call.message.edit_reply_markup(await get_cart_keyboard(data["page_num"]))


@dp.callback_query_handler(text="previous", state=CartListing.CartWatching)
async def show_next_page(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data["page_num"] > 0:
            data["page_num"] -= 1
            await call.message.edit_reply_markup(await get_cart_keyboard(data["page_num"]))


@dp.callback_query_handler(state=CartListing.CartWatching)
async def show_product(call: CallbackQuery, state: FSMContext):
    await CartListing.ProductWatching.set()
    cart_record_id = call.data
    cart_record = await db.get_cart_record(int(cart_record_id))
    product_id = cart_record["product_id"]

    product = await db.get_product(int(product_id))
    images = await get_product_images(int(product_id))
    if images:
        for path in images:
            await call.message.answer_photo(InputFile(path))

    text = f"{product['name']}\n{product['description']}"
    number_text = f'{cart_record["number"]} шт.'
    await call.message.answer(text)
    await call.message.answer(number_text, reply_markup=cart_record_watching)

    await state.update_data({"cart_record_id": cart_record_id})


@dp.callback_query_handler(text="decrease", state=CartListing.ProductWatching)
async def decrease_cart_record(call: CallbackQuery, state: FSMContext):
    cart_record_id = (await state.get_data()).get("cart_record_id")
    cart_record = await db.get_cart_record(int(cart_record_id))
    if not cart_record:
        return

    number_text = '{} шт.'
    if cart_record["number"] <= 1:
        await state.update_data({"product_id": cart_record["product_id"]})
        await db.delete_from_cart(int(cart_record["product_id"]))
        await call.message.edit_text("Удалено.", reply_markup=cart_record_watching)
    else:
        new_number = cart_record["number"] - 1
        await db.change_from_cart(int(cart_record["product_id"]), new_number)
        await call.message.edit_text(number_text.format(new_number), reply_markup=cart_record_watching)


@dp.callback_query_handler(text="increase", state=CartListing.ProductWatching)
async def increase_cart_record(call: CallbackQuery, state: FSMContext):
    cart_record_id = (await state.get_data()).get("cart_record_id")
    cart_record = await db.get_cart_record(int(cart_record_id))

    number_text = '{} шт.'
    if not cart_record:
        new_number = 1
        product_id = (await state.get_data()).get("product_id")
        new_id = await db.add_to_cart(product_id, new_number)
        await state.update_data({"cart_record_id": new_id})
    else:
        new_number = cart_record["number"] + 1
        await db.change_from_cart(int(cart_record["product_id"]), new_number)

    await call.message.edit_text(number_text.format(new_number), reply_markup=cart_record_watching)


@dp.callback_query_handler(text="cart", state=CartListing.ProductWatching)
async def show_cart(call: CallbackQuery, state: FSMContext):
    await CartListing.CartWatching.set()
    data = await state.get_data()
    await call.message.answer("Ваша корзина: ", reply_markup=await get_cart_keyboard(data["page_num"]))
