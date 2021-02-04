from aiogram.types import Message
from aiogram.dispatcher.filters import Command, Text
from keyboards.default import main_menu_kb

from loader import dp


@dp.message_handler(Command("menu"))
async def show_menu(message: Message):
    await message.answer("Вам доступна навигация по меню:", reply_markup=main_menu_kb)


@dp.message_handler(Text(ignore_case=True, contains=['оформить заказ']))
async def checkout(message: Message):
    await message.answer("Ваша корзина пуста.", reply_markup=main_menu_kb)
