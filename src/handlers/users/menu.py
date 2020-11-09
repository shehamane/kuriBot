from loader import dp
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.dispatcher.filters import Command, Text
from keyboards.default import menu


@dp.message_handler(Command("menu"))
async def show_menu(message: Message):
    await message.answer("Добрый день! Вам доступна навигация по меню:", reply_markup=menu)


@dp.message_handler(Text(contains=['корзина']))
async def show_cart(message: Message):
    await message.answer("Ваша корзина пуста.")


@dp.message_handler(Text(contains=['каталог']))
async def show_cart(message: Message):
    await message.answer("Все товары распроданы.")


@dp.message_handler(Text(contains=['оформить заказ']))
async def show_cart(message: Message):
    await message.answer("Ваша корзина пуста.")
