from aiogram.types import Message

from filters.is_user import IsNotUserFilter

from loader import dp


@dp.message_handler(IsNotUserFilter())
async def shrug(message: Message):
    await message.answer("Вы не зарегестрированы в базах. Отправьте /start, чтобы зарегестрироваться.")
