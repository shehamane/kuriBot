from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data import config

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

from asyncio import get_event_loop
from utils.db_api.conn import create_db

loop = get_event_loop()
db_pool = loop.run_until_complete(create_db())

