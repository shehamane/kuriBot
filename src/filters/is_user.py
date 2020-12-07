from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message

from utils.db_api.api import db


class IsUserFilter(BoundFilter):
    async def check(self, message: Message) -> bool:
        return not await db.get_id()
