from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp
from utils.misc import rate_limit


@rate_limit(5, 'help')
@dp.message_handler(Text(contains=['помощь'], ignore_case=True))
@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    text = [
        'Список команд: ',
        '/start - Начать диалог',
        '/help - Получить справку',
        '/menu - Открыть меню',
        '/admin - Панель администратора',
        'Для отмены любого действия пишите "отмена"'
    ]
    await message.answer('\n'.join(text))
