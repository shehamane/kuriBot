from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from keyboards.inline import get_orders_kb
from keyboards.inline.general import back_button
from states import Orders

from loader import dp
from utils.callback_datas import choose_order_cd
from utils.db_api.api import db_api as db


@dp.message_handler(Text(contains=['мои заказы'], ignore_case=True), state='*')
async def show_orders(message: Message, state: FSMContext):
    await state.finish()
    await Orders.OrderList.set()
    await message.answer("Ваши заказы:", reply_markup=await get_orders_kb(await db.get_orders()))


@dp.callback_query_handler(choose_order_cd.filter(), state=Orders.OrderList)
async def show_order_info(call: CallbackQuery, callback_data: dict):
    await Orders.OrderInfo.set()

    order = await db.get_order(int(callback_data["order_id"]))
    cart_items = await db.get_cart_items_by_cart(order.cart_id)

    text = f"ЗАКАЗ ОТ {order.date}\n\n"
    for cart_item in cart_items:
        product = await db.get_product(cart_item.product_id)
        text += f"{product.name} x {cart_item.amount}\n"
    text += f"\nСумма: {order.price}р.\n"

    await call.message.edit_text(text, reply_markup=back_button)


@dp.callback_query_handler(text="back", state=Orders.OrderInfo)
async def back_to_orders_list(call: CallbackQuery):
    await Orders.OrderList.set()

    await call.message.edit_text("Ваши заказы:", reply_markup=await get_orders_kb(await db.get_orders()))
