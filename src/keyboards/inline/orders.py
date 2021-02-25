from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.db_api.api import db_api as db


async def get_orders_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    carts = await db.get_orders()

    for cart_id in carts:
        kb.inline_keyboard.append([
            InlineKeyboardButton(text="Заказ", callback_data=cart_id[0])
        ])
    return kb
