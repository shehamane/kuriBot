from aiogram.types import Message
from aiogram.dispatcher.filters import Command
from keyboards.default import main_menu_kb

from loader import dp


@dp.message_handler(Command("menu"))
async def show_menu(message: Message):
    await message.answer("Вам доступна навигация по меню:", reply_markup=main_menu_kb)
