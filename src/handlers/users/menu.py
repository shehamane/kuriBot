from loader import dp
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.dispatcher.filters import Command, Text
from keyboards.default import menu


@dp.message_handler(Command("menu"))
async def show_menu(message: Message):
    await message.answer("Добрый день! Вам доступна навигация по меню:", reply_markup=menu)


@dp.message_handler(Text(ignore_case=True, contains=['корзина']))
async def show_cart(message: Message):
    await message.answer("Ваша корзина пуста.", reply_markup=menu)


@dp.message_handler(Text(ignore_case=True, contains=['каталог']))
async def show_cart(message: Message):
    await message.answer("Все товары распроданы.", reply_markup=menu)


@dp.message_handler(Text(ignore_case=True, contains=['оформить заказ']))
async def show_cart(message: Message):
    await message.answer("Ваша корзина пуста.", reply_markup=menu)
