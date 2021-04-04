from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from filters.is_numeric import IsNumericFilterCallback
from keyboards.inline import get_orders_kb
from keyboards.inline.general import back_kb
from states import Orders

from loader import dp
from utils.db_api.api import db_api as db


@dp.message_handler(Text(contains=['мои заказы'], ignore_case=True), state='*')
async def show_orders(message: Message, state: FSMContext):
    await state.finish()
    await Orders.OrderList.set()
    await message.answer("Ваши заказы:", reply_markup=await get_orders_kb(await db.get_orders()))


@dp.callback_query_handler(IsNumericFilterCallback(), state=Orders.OrderList)
async def show_order_info(call: CallbackQuery):
    await Orders.OrderInfo.set()

    order = await db.get_order(int(call.data))
    cart_items = await db.get_cart_items_by_cart(order.cart_id)

    text = f"ЗАКАЗ ОТ {order.date}\n\n"
    to_pay = 0
    for cart_item in cart_items:
        product = await db.get_product(cart_item.product_id)
        text += f"{product.name} x {cart_item.amount} \t\t\t\t\t {product.price * cart_item.amount}р.\n"
        to_pay += product.price * cart_item.amount
    text += f"\nСумма: {to_pay}р.\n"

    await call.message.edit_text(text, reply_markup=back_kb)


@dp.callback_query_handler(text="back", state=Orders.OrderInfo)
async def back_to_orders_list(call: CallbackQuery):
    await Orders.OrderList.set()

    await call.message.edit_text("Ваши заказы:", reply_markup=await get_orders_kb(await db.get_orders()))
