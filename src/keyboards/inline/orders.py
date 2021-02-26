from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.db_api.api import db_api as db


async def get_orders_kb(user_id=None):
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    orders = await db.get_orders(user_id)

    for order_id, date, price in orders:
        kb.inline_keyboard.append([
            InlineKeyboardButton(text=f"Заказ от {date}, {price}р.", callback_data=order_id)
        ])
    kb.inline_keyboard.append([
        InlineKeyboardButton(text="Отмена", callback_data="cancel")
    ])
    return kb
