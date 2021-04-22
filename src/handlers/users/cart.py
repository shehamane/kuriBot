from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, InputFile, InputMediaPhoto

from keyboards.inline import get_cart_item_operating_kb, get_cart_kb, confirmation_kb
from utils.callback_datas import choose_cart_item_cd

from utils.misc.files import get_product_image_path
from utils.db_api.api import db_api as db

from states import Cart

from data.api_config import CART_PAGE_VOLUME
from data.media_config import IMG_CART_PATH, IMG_DEFAULT_PATH

from loader import dp


@dp.message_handler(Text(contains=['корзина'], ignore_case=True), state='*')
async def show_cart(message: Message, state: FSMContext):
    await state.finish()
    await Cart.CartItems.set()

    await state.update_data({"page_num": 0})
    await message.answer_photo(InputFile(IMG_CART_PATH), caption="Ваша корзина: ",
                               reply_markup=await get_cart_kb(await db.get_cart_page(0)))


@dp.callback_query_handler(text="next", state=Cart.CartItems)
async def show_next_page(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data["page_num"] < int(await db.count_cart() / (CART_PAGE_VOLUME + 1)):
            data["page_num"] += 1
            await call.message.edit_reply_markup(await get_cart_kb(await db.get_cart_page(data["page_num"])))


@dp.callback_query_handler(text="previous", state=Cart.CartItems)
async def show_previous_page(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data["page_num"] > 0:
            data["page_num"] -= 1
            await call.message.edit_reply_markup(await get_cart_kb(await db.get_cart_page(data["page_num"])))


@dp.callback_query_handler(text="clear", state=Cart.CartItems)
async def confirm_deletion(call: CallbackQuery):
    await Cart.ClearConfirmation.set()
    await call.message.edit_caption("Ваша корзина будет очищена. Продолжить?", reply_markup=confirmation_kb)


@dp.callback_query_handler(text="no", state=Cart.ClearConfirmation)
async def show_cart(call: CallbackQuery, state: FSMContext):
    await Cart.CartItems.set()
    async with state.proxy() as data:
        await call.message.edit_caption("Ваша корзина:",
                                        reply_markup=await get_cart_kb(await db.get_cart_page(data["page_num"])))


@dp.callback_query_handler(text="yes", state=Cart.ClearConfirmation)
async def clear_cart(call: CallbackQuery):
    await Cart.CartItems.set()
    await db.clear_cart()
    await call.message.edit_caption("Корзина очищена", reply_markup=await get_cart_kb(await db.get_cart_page(0)))


@dp.callback_query_handler(choose_cart_item_cd.filter(), state=Cart.CartItems)
async def show_cart_item(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await Cart.ItemInfo.set()

    cart_item_id = int(callback_data.get("cart_item_id"))
    cart_item = await db.get_cart_item(cart_item_id)
    await state.update_data({"cart_item_id": cart_item_id})

    product = await db.get_product(cart_item.product_id)

    text = f"{product.name}\n" \
           f"{product.description}\n" \
           f"{product.price} р."

    img_path = await get_product_image_path(product.id)
    if not img_path:
        img_path = IMG_DEFAULT_PATH
    await call.message.edit_media(InputMediaPhoto(InputFile(img_path)))
    await call.message.edit_caption(text, reply_markup=await get_cart_item_operating_kb(cart_item.amount))


@dp.callback_query_handler(text="decrease", state=Cart.ItemInfo)
async def decrease_amount(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        cart_item = await db.get_cart_item(int(state_data["cart_item_id"]))

    if not cart_item:
        return

    if cart_item.amount <= 1:
        new_number = 0
        await state.update_data({"deleted_product_id": cart_item.product_id})
        await db.delete_cart_item(int(cart_item.id))
        await call.message.edit_reply_markup(reply_markup=await get_cart_item_operating_kb(0))
    else:
        new_number = cart_item.amount - 1
        await cart_item.update(amount=new_number).apply()

    await call.message.edit_reply_markup(reply_markup=await get_cart_item_operating_kb(new_number))


@dp.callback_query_handler(text="increase", state=Cart.ItemInfo)
async def increase_cart_item(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        cart_item = await db.get_cart_item(int(state_data["cart_item_id"]))

    if not cart_item:
        new_number = 1
        product_id = (await state.get_data()).get("deleted_product_id")
        new_item = await db.create_cart_item(product_id, 1)
        await state.update_data({"cart_item_id": new_item.id})
    else:
        new_number = cart_item.amount + 1
        await cart_item.update(amount=new_number).apply()

    await call.message.edit_reply_markup(reply_markup=await get_cart_item_operating_kb(new_number))


@dp.callback_query_handler(text="delete", state=Cart.ItemInfo)
async def delete_cart_item(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        cart_item = await db.get_cart_item(int(state_data["cart_item_id"]))

    if not cart_item:
        return

    await state.update_data({"deleted_product_id": cart_item.product_id})
    await db.delete_cart_item(int(cart_item.id))

    await call.message.edit_reply_markup(reply_markup=await get_cart_item_operating_kb(0))


@dp.callback_query_handler(text="back", state=Cart.ItemInfo)
async def show_cart(call: CallbackQuery, state: FSMContext):
    await Cart.CartItems.set()
    data = await state.get_data()
    await call.message.edit_media(InputMediaPhoto(InputFile(IMG_CART_PATH)))
    await call.message.edit_caption(caption="Ваша корзина: ",
                                    reply_markup=await get_cart_kb(await db.get_cart_page(data["page_num"])))
