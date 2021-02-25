from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.db_api.api import db_api as db


async def get_orders_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    orders = await db.get_orders()

    for cart_id, date, price in orders:
        kb.inline_keyboard.append([
            InlineKeyboardButton(text=f"Заказ от {date}, {price}р.", callback_data=cart_id)
        ])
    return kb
