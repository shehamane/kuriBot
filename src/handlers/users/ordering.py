from datetime import datetime

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery, ContentType, ShippingQuery

from data.config import PAYMENT_TOKEN
from data.shop_config import IS_PREPAYMENT, CURRENCY, NEED_NAME, NEED_EMAIL, NEED_PHONE_NUMBER, NEED_SHIPPING_ADDRESS, \
    RUSSIAN_POST_SHIPPING_OPTION, PICKUP_SHIPPING_OPTION
from filters.is_numeric import IsNumericFilter
from keyboards.inline.general import confirmation_kb, confirmation_cancel_kb
from loader import dp, bot
from states.ordering import Ordering
from utils.db_api.api import db_api as db


@dp.callback_query_handler(text="order", state='*')
async def order(call: CallbackQuery):
    await confirm_address(call.message)


@dp.message_handler(Text(ignore_case=True, contains=['оформить заказ']), state='*')
async def confirm_address(message: Message):
    if not await db.count_cart():
        await message.answer("Ваша корзина пуста!")
        return
    user = await db.get_current_user()
    await message.answer(f"Адрес доставки: {user.address}", reply_markup=confirmation_kb)

    await Ordering.AddressConfirmation.set()


@dp.callback_query_handler(text="no", state=Ordering.AddressConfirmation)
async def request_address(call: CallbackQuery):
    await call.message.edit_text("Введите адрес доставки...")

    await Ordering.AddressRequest.set()


@dp.message_handler(state=Ordering.AddressRequest)
async def change_address(message: Message):
    user = await db.get_current_user()
    await user.update(address=message.text).apply()

    await confirm_address(message)


@dp.callback_query_handler(text="yes", state=Ordering.AddressConfirmation)
async def confirm_phone_number(call: CallbackQuery):
    user = await db.get_current_user()
    await call.message.answer(f"Номер телефона: {user.phone_number}", reply_markup=confirmation_kb)

    await Ordering.PhoneNumberConfirmation.set()


@dp.callback_query_handler(text="no", state=Ordering.PhoneNumberConfirmation)
async def request_phone_number(call: CallbackQuery):
    await call.message.edit_text("Введите ваш номер телефона (11 цифр без пробелов, дефисов и скобок)...")

    await Ordering.PhoneNumberRequest.set()


@dp.message_handler(IsNumericFilter(), state=Ordering.PhoneNumberRequest)
async def change_phone_number(message: Message):
    if len(message.text) != 11:
        await message.answer("Номер должен содержать 11 цифр")
        return
    user = await db.get_current_user()
    await user.update(phone_number=message.text).apply()

    await message.answer(f"Номер телефона: {user.phone_number}", reply_markup=confirmation_kb)
    await Ordering.PhoneNumberConfirmation.set()


@dp.callback_query_handler(text="yes", state=Ordering.PhoneNumberConfirmation)
async def confirm_cart(call: CallbackQuery, state: FSMContext):
    user = await db.get_current_user()
    cart = await db.get_cart_items_by_user(user.id)

    text = "===============ЗАКАЗ===============\n\n"
    to_pay = 0
    prices = []
    for record in cart:
        product = await db.get_product(record.product_id)
        text += f"{product.name} x {record.amount} \t\t\t\t\t {product.price * record.amount}р.\n"
        to_pay += product.price * record.amount
        prices.append(
            LabeledPrice(label=product.name + f" x {record.amount}", amount=product.price * record.amount * 100))

    async with state.proxy() as data:
        data["prices"] = prices

    text += f"\nСумма: {to_pay}р.\n" \
            f"Адрес доставки: {user.address}\n" \
            f"Номер телефона: {user.phone_number}\n" \
            f"Оформить заказ?"

    await call.message.answer(text, reply_markup=confirmation_cancel_kb)
    await Ordering.OrderConfrimation.set()


@dp.callback_query_handler(text="yes", state=Ordering.OrderConfrimation)
async def create_order(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        prices = data["prices"]

    if IS_PREPAYMENT:
        await call.message.answer("Оплатите сумму заказа")
        await bot.send_invoice(chat_id=call.from_user.id, title=f"ЗАКАЗ ОТ {datetime.today()}",
                               description='Или введите "Отмена"',
                               payload=0, start_parameter=0, currency=CURRENCY,
                               prices=prices,
                               provider_token=PAYMENT_TOKEN,
                               need_name=NEED_NAME,
                               need_email=NEED_EMAIL,
                               need_phone_number=NEED_PHONE_NUMBER,
                               need_shipping_address=NEED_SHIPPING_ADDRESS,
                               is_flexible=True)
        await Ordering.Payment.set()
    else:
        await db.create_order()
        await call.message.answer("Заказ оформлен!")
        await state.finish()


@dp.pre_checkout_query_handler(lambda query: True, state=Ordering.Payment)
async def checkout(query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, True)


@dp.shipping_query_handler(lambda query: True, state=Ordering.Payment)
async def process_shipping_query(query: ShippingQuery):
    await bot.answer_shipping_query(query.id, ok=True, shipping_options=[
        RUSSIAN_POST_SHIPPING_OPTION,
        PICKUP_SHIPPING_OPTION])


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT, state=Ordering.Payment)
async def proceed_successful_payment(message: Message, state: FSMContext):
    await db.create_order()
    await bot.send_message(chat_id=message.from_user.id, text="Спасибо за покупку!")
    await state.finish()
