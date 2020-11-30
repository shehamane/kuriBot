from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram import types

from loader import dp


@dp.message_handler(ChatTypeFilter(chat_type="group"))
async def shrug_group(message: types.Message):
    await message.answer("Бот временно недоступен в группах:(")


@dp.message_handler(ChatTypeFilter(chat_type="supergroup"))
async def shrug_group(message: types.Message):
    await message.answer("Бот временно недоступен в группах:(")
