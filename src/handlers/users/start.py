from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp
from utils.db_api.new_api import db_api as db


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.answer(f'Привет, {message.from_user.full_name}!')
    user = await db.create_user()

    text = "Для вызова меню пиши /menu"
    await message.answer(text)
