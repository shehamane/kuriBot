from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.db_api.api import db_api as db

async def get_cart_record_watching_kb(amount):
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


async def get_cart_keyboard(page_list):
    to_pay = 0

    # if len(page_list) == 0 and page_num > 0:
    #     page_num -= 1
    #     cart_list = await db.get_cart_list(page_num)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[

        ]
    )
    for cart_record in page_list:
        product = await db.get_product(cart_record.product_id)
        to_pay += cart_record.amount * product.price

        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(text=f"{product.name} - {cart_record.amount} шт.",
                                     callback_data=str(cart_record.id)),
                InlineKeyboardButton(text=f"{cart_record.amount * product.price} р.", callback_data="amount")
            ]
        )

    keyboard.inline_keyboard.append(
        [
            InlineKeyboardButton(text="<", callback_data="previous"),
            InlineKeyboardButton(text="Отмена", callback_data="cancel"),
            InlineKeyboardButton(text=">", callback_data="next")
        ]
    )
    keyboard.inline_keyboard.append(
        [
            InlineKeyboardButton(text=f"Итого: {to_pay} р.", callback_data="to_pay"),
            InlineKeyboardButton(text=f"Оформить заказ", callback_data="checkout")
        ]
    )
    return keyboard
