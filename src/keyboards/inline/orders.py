from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.db_api.api import db_api as db


async def get_orders_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    orders = await d