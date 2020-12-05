from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message


class IsNumericFilter(BoundFilter):
    async def check(self, message: Message) -> bool:
        return message.text.isnumeric()