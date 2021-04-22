from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.callback_datas import choose_order_cd
from utils.db_api.api import Order


async def get_orders_kb(orders: [Order]):
    kb = InlineKeyboardMarkup(inline_keyboard=[])

    for order in orders:
        kb.inline_keyboard.append([
            InlineKeyboardButton(text=f"Заказ от {order.date}, {order.price}р.",
                                 callback_data=choose_order_cd.new(order_id=order.id))
        ])
    return kb
