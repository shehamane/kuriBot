from aiogram.types import Message

from loader import dp


@dp.message_handler()
async def shrug(message: Message):
    await message.answer("не понял.")
