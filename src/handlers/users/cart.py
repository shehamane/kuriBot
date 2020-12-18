from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, InputFile, InputMediaPhoto

from filters.is_numeric import IsNumericFilterCallback
from keyboards.inline import get_cart_record_watching_kb, get_cart_keyboard
from states import CartListing

from loader import dp
from utils.db_api.api import db

from data.api_config import PAGE_VOLUME
from data.media_config import IMG_CART_PATH
from utils.misc.files import get_product_image_path


@dp.message_handler(Text(contains=['корзина'], ignore_case=True), state='*')
async def show_cart(message: Message, state: FSMContext):
    await state.finish()
    await CartListing.CartWatching.set()

    await state.update_data({"page_num": 0})

    await message.answer_photo(InputFile(IMG_CART_PATH), caption="Ваша корзина: ",
                               reply_markup=await get_cart_keyboard(db, 0))


@dp.callback_query_handler(text="next", state=CartListing.CartWatching)
async def show_next_page(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data["page_num"] < int(await db.count_cart() / (PAGE_VOLUME + 1)):
            data["page_num"] += 1
            await call.message.edit_reply_markup(await get_cart_keyboard(db, data["page_num"]))


@dp.callback_query_handler(text="previous", state=CartListing.CartWatching)
async def show_next_page(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data["page_num"] > 0:
            data["page_num"] -= 1
            await call.message.edit_reply_markup(await get_cart_keyboard(db, data["page_num"]))


@dp.callback_query_handler(IsNumericFilterCallback(), state=CartListing.CartWatching)
async def show_product(call: CallbackQuery, state: FSMContext):
    await CartListing.ProductWatching.set()

    cart_record_id = int(call.data)
    cart_record = await db.get_cart_record(cart_record_id)

    product_id = int(cart_record["product_id"])
    product = await db.get_product(product_id)

    text = f"{product['name']}\n{product['description']}"

    img_path = await get_product_image_path(product_id)
    if img_path:
        await call.message.edit_media(InputMediaPhoto(InputFile(img_path)))
        await call.message.edit_caption(text, reply_markup=await get_cart_record_watching_kb(cart_record["amount"]))
    await state.update_data({"cart_record_id": cart_record_id})


@dp.callback_query_handler(text="decrease", state=CartListing.ProductWatching)
async def decrease_cart_record(call: CallbackQuery, state: FSMContext):
    cart_record_id = (await state.get_data()).get("cart_record_id")
    cart_record = await db.get_cart_record(int(cart_record_id))

    if not cart_record:
        return

    if cart_record["amount"] <= 1:
        await state.update_data({"product_id": cart_record["product_id"]})
        await db.delete_from_cart(int(cart_record["product_id"]))
        await call.message.edit_reply_markup(reply_markup=await get_cart_record_watching_kb(0))
    else:
        new_number = cart_record["amount"] - 1
        await db.change_from_cart(int(cart_record["product_id"]), new_number)
        await call.message.edit_reply_markup(reply_markup=await get_cart_record_watching_kb(new_number))


@dp.callback_query_handler(text="increase", state=CartListing.ProductWatching)
async def increase_cart_record(call: CallbackQuery, state: FSMContext):
    cart_record_id = (await state.get_data()).get("cart_record_id")
    cart_record = await db.get_cart_record(int(cart_record_id))

    if not cart_record:
        new_number = 1

        product_id = (await state.get_data()).get("product_id")
        new_id = await db.add_to_cart(product_id, new_number)

        await state.update_data({"cart_record_id": new_id})
    else:
        new_number = cart_record["amount"] + 1

        await db.change_from_cart(int(cart_record["product_id"]), new_number)

    await call.message.edit_reply_markup(reply_markup=await get_cart_record_watching_kb(new_number))


@dp.callback_query_handler(text="delete", state=CartListing.ProductWatching)
async def delete_cart_record(call: CallbackQuery, state: FSMContext):
    cart_record_id = (await state.get_data()).get("cart_record_id")
    cart_record = await db.get_cart_record(int(cart_record_id))

    if not cart_record:
        return

    await state.update_data({"product_id": cart_record["product_id"]})
    await db.delete_from_cart(int(cart_record["product_id"]))

    await call.message.edit_reply_markup(reply_markup=await get_cart_record_watching_kb(0))


@dp.callback_query_handler(text="cart", state=CartListing.ProductWatching)
async def show_cart(call: CallbackQuery, state: FSMContext):
    await CartListing.CartWatching.set()
    data = await state.get_data()
    await call.message.edit_media(InputMediaPhoto(InputFile(IMG_CART_PATH)))
    await call.message.edit_caption(caption="Ваша корзина: ",
                                    reply_markup=await get_cart_keyboard(db, 0))
