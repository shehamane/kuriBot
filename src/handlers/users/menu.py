from aiogram.types import Message
from aiogram.dispatcher.filters import Command, Text
from keyboards.default import menu

from loader import dp
from utils.db_api.api import db


@dp.message_handler(Command("menu"))
async def show_menu(message: Message):
    await message.answer("Добрый день! Вам доступна навигация по меню:", reply_markup=menu)


@dp.message_handler(Text(ignore_case=True, contains=['оформить заказ']))
async def checkout(message: Message):
    await message.answer("Ваша корзина пуста.", reply_markup=menu)
