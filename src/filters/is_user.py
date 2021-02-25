from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message

from utils.db_api.api import db_api


class IsNotUserFilter(BoundFilter):
    async def check(self, message: Message) -> bool:
        return not await db_api.get_id()
