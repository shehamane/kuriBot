from aiogram.types import Message

from filters.is_user import IsNotUserFilter
from loader import dp
from utils.db_api.api import db_api as db


@dp.message_handler(IsNotUserFilter())
async def shrug(message: Message):
    await message.answer("Вы не зарегестрированы в базах. Отправьте /start, чтобы зарегестрироваться.")