from aiogram.types import Message
from aiogram.dispatcher.filters import Command
from keyboards.default import admin_panel_kb

from loader import dp


@dp.message_handler(Command("admin"))
async def show_admin_panel(message: Message):
    await message.answer('Вы вошли в панель администратора. Отправьте "отмена" для выхода', reply_markup=admin_panel_kb)
