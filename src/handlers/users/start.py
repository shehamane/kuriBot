from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp
from utils.db_api.api import db


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.answer(f'Привет, {message.from_user.full_name}!')
    id = await db.add_new_user()
    users_num = await db.count_users()

    text = ""
    if not id:
        id = await db.get_id()
    else:
        text += "Вы успешно добавлены в базу!\n"

    num_ending = "" if (users_num>9 and users_num < 20) or (users_num%10 <1 and users_num%10>5) else "a"
    text += f"Сейчас в базе {users_num} человек" + num_ending + ".\n"
    await message.answer(text)
