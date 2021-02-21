from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import InlineKeyboardButton, CallbackQuery, Message

from filters.is_alpha import IsAlphaFilterCallback, IsAlphaFilter
from filters.is_numeric import IsNumericFilterCallback, IsNumericFilter
from keyboards.default import main_menu_kb
from keyboards.inline import registration_kb
from keyboards.inline.registration import register_kb
from loader import dp
from states.registration import Registration
from utils.db_api.api import db_api as db


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message, state: FSMContext):
    msg = await message.answer(f'Привет, {message.from_user.full_name}!\n'
                               f'Зарегестриуйся в системе...',
                               reply_markup=register_kb)
    await state.update_data({"user": await db.create_user(),
                             "reg_message": msg})


@dp.callback_query_handler(text="register")
async def send_registration_page(call: CallbackQuery, state: FSMContext):
    await Registration.Menu.set()

    await call.message.edit_text("Введите информацию в следующие поля:",
                                 reply_markup=registration_kb)


@dp.callback_query_handler(text="name", state=Registration.Menu)
async def request_name(call: CallbackQuery, state: FSMContext):
    await Registration.NameRequest.set()

    await call.message.edit_text("Введите ваше настоящее имя...")


@dp.message_handler(IsAlphaFilter(), state=Registration.NameRequest)
async def set_name(message: Message, state: FSMContext):
    async with state.proxy() as state_data:
        await state_data["user"].update(fullname=message.text).apply()

        await state_data["reg_message"].edit_text("Введите информацию в следующие поля:",
                                                  reply_markup=registration_kb)

    await Registration.Menu.set()


@dp.callback_query_handler(text="phone_number", state=Registration.Menu)
async def phone_number_request(call: CallbackQuery, state: FSMContext):
    await Registration.PhoneRequest.set()

    await call.message.edit_text("Введите ваш номер телефона (11 цифр)")


@dp.message_handler(IsNumericFilter(), state=Registration.PhoneRequest)
async def set_phone_number(message: Message, state: FSMContext):
    async with state.proxy() as state_data:
        if len(message.text) != 11:
            await state_data["reg_message"].edit_text("Номер должен содержать 11 цифр. Повторите попытку")
            return
        await state_data["user"].update(phone_number=message.text).apply()

        await state_data["reg_message"].edit_text("Введите информацию в следующие поля:",
                                                  reply_markup=registration_kb)

    await Registration.Menu.set()


@dp.callback_query_handler(text="address", state=Registration.Menu)
async def phone_number_request(call: CallbackQuery, state: FSMContext):
    await Registration.AddressRequest.set()

    await call.message.edit_text("Введите ваш адрес")


@dp.message_handler(state=Registration.AddressRequest)
async def set_phone_number(message: Message, state: FSMContext):
    async with state.proxy() as state_data:
        await state_data["user"].update(address=message.text).apply()

        await state_data["reg_message"].edit_text("Введите информацию в следующие поля:",
                                                  reply_markup=registration_kb)

    await Registration.Menu.set()


@dp.callback_query_handler(text="finish", state=Registration.Menu)
async def check_info(call: CallbackQuery, state: FSMContext):
    text = ""
    async with state.proxy() as state_data:
        user = state_data["user"]

    if not user.fullname:
        text += "ваше имя\n"
    if not user.phone_number:
        text += "телефонный номер\n"
    if not user.address:
        text += "адрес доставки\n"

    if text:
        await call.message.edit_text("Вы не ввели:\n" + text, reply_markup=registration_kb)
    else:
        await call.message.edit_text("Регистрация успешно завершена!\n"
                                     "Пиши /menu")
        await state.finish()
