from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message, CallbackQuery


class IsAlphaFilter(BoundFilter):
    async def check(self, message: Message) -> bool:
        return message.text.isalpha()


class IsAlphaFilterCallback(BoundFilter):
    async def check(self, call: CallbackQuery) -> bool:
        return call.data.isalpha()
