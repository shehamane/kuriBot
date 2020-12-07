from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message


class IsPositiveFilter(BoundFilter):
    async def check(self, message: Message) -> bool:
        return message.text.isnumeric() and int(message.text) > 0
