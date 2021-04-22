from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import CallbackQuery, Message

from filters.is_user import IsNotUserFilter

from keyboards.inline import start_button

from loader import dp
from utils.db_api.api import db_api as db


@dp.message_handler(IsNotUserFilter())
async def greet(message: Message):
    await message.answer("Привет! Для начала нажмите на кнопку ниже:", reply_markup=start_button)


@dp.callback_query_handler(text="start")
async def start_with_button(call: CallbackQuery):
    await start(call.message)


@dp.message_handler(CommandStart())
async def start(message: types.Message):
    user = await db.create_user()
    await message.answer(f"Привет, {user.username}! Для получения нажмите 'Помощь' или введите '/help'")
