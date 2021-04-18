from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.callback_datas import choose_cart_item_cd


async def get_cart_item_operating_kb(amount):
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
                InlineKeyboardButton(text="Назад", callback_data="back"),
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
                                     callback_data=choose_cart_item_cd.new(cart_item_id=item_id)),
                InlineKeyboardButton(text=f"{amount * price} р.",
                                     callback_data=choose_cart_item_cd.new(cart_item_id=item_id)),
            ]
        )

    keyboard.inline_keyboard.append(
        [
            InlineKeyboardButton(text="<", callback_data="previous"),
            InlineKeyboardButton(text="Очистить", callback_data="clear"),
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
