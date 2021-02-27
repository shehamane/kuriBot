from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.db_api.api import db_api as db, CartItem


async def get_cart_item_watching_kb(amount):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f"{amount} шт.", callback_data="amount")
            ],
            [
                InlineKeyboardButton(text="-", callback_data="decrease"),
                InlineKeyboardButton(text="+", callback_data="increase"),
            ],
            [
                InlineKeyboardButton(text="Удалить", callback_data="delete"),
            ],
            [
                InlineKeyboardButton(text="Вернуться в корзину", callback_data="cart"),
            ],
        ]
    )


async def get_cart_kb(cart_items_info):
    to_pay = 0

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for name, price, item_id, amount in cart_items_info:
        to_pay += amount * price

        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(text=f"{name} x {amount}",
                                     callback_data=str(item_id)),
                InlineKeyboardButton(text=f"{amount * price} р.",
                                     callback_data=str(item_id))
            ]
        )

    keyboard.inline_keyboard.append(
        [
            InlineKeyboardButton(text="<", callback_data="previous"),
            InlineKeyboardButton(text="Отмена", callback_data="cancel"),
            InlineKeyboardButton(text=">", callback_data="next")
        ],
    )
    keyboard.inline_keyboard.append(
        [
            InlineKeyboardButton(text=f"Итого: {to_pay} р.", callback_data="to_pay"),
            InlineKeyboardButton(text=f"Оформить заказ", callback_data="order")
        ]
    )
    return keyboard
