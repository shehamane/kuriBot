from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from aiogram.dispatcher.filters import Command
from keyboards.default import admin_panel_kb

from loader import dp
from states import AdminPanel


@dp.message_handler(Command("admin"))
async def show_admin_panel(message: Message, state: FSMContext):
    await state.finish()
    await AdminPanel.AdminPanel.set()

    await message.answer('Вы вошли в панель администратора. Отправьте "отмена" для выхода', reply_markup=admin_panel_kb)
