from aiogram import types
from loader import dp


@dp.message_handler()
async def shrug(message: types.Message):
    await message.answer("не понял.")
