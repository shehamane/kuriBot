from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from filters.is_numeric import IsNumericFilter
from keyboards.default import main_menu_kb
from keyboards.inline.general import confirmation_kb, confirmation_cancel_kb
from loader import dp
from states.ordering import Ordering
from utils.db_api.api import db_api as db


@dp.callback_query_handler(text="order", state='*')
async def order(call: CallbackQuery):
    await confirm_address(call.message)


@dp.message_handler(Text(ignore_case=True, contains=['оформить заказ']), state='*')
async def confirm_address(message: Message):
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
async def confirm_cart(call: CallbackQuery):
    user = await db.get_current_user()
    cart = await db.get_cart_by_id(user.id)

    text = "===============ЗАКАЗ===============\n\n"
    to_pay = 0
    for record in cart:
        product = await db.get_product(record.product_id)
        text += f"{product.name} x {record.amount} \t\t\t\t\t {product.price * record.amount}р.\n"
        to_pay += product.price * record.amount

    text += f"\nСумма: {to_pay}р.\n" \
            f"Адрес доставки: {user.address}\n" \
            f"Номер телефона: {user.phone_number}\n" \
            f"Оформить заказ?"

    await call.message.answer(text, reply_markup=confirmation_cancel_kb)
    await Ordering.OrderConfrimation.set()

@dp.callback_query_handler(text="yes", state=Ordering.OrderConfrimation)
async def create_order(call: CallbackQuery, state: FSMContext):
    await db.create_order()
    await call.message.answer("Заказ оформлен!")
    await state.finish()
