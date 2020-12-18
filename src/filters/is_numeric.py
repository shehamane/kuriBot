from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message, CallbackQuery


class IsNumericFilter(BoundFilter):
    async def check(self, message: Message) -> bool:
        return message.text.isnumeric()


class IsNumericFilterCallback(BoundFilter):
    async def check(self, call: CallbackQuery) -> bool:
        return call.data.isnumeric()
