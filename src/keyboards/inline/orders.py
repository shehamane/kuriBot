from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.db_api.api import Order


async def get_orders_kb(orders: [Order]):
    kb = InlineKeyboardMarkup(inline_keyboard=[])

    for order in orders:
        kb.inline_keyboard.append([
            InlineKeyboardButton(text=f"Заказ от {order.date}, {order.price}р.", callback_data=order.id)
        ])
    return kb
