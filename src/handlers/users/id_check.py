from aiogram.types import Message

from filters.is_user import IsUserFilter
from loader import dp
from utils.db_api.api import db_api as db


@dp.message_handler(IsUserFilter())
async def shrug(message: Message):
    id = await db.get_id()
    if not id:
        await message.answer("Вы не зарегестрированы в базах. Отправьте /start, чтобы зарегестрироваться.")