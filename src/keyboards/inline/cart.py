from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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


async def get_cart_keyboard(db, page_num):
    cart_list = await db.get_cart_list(page_num)

    if len(cart_list) == 0 and page_num > 0:
        page_num -= 1
        cart_list = await db.get_cart_list(page_num)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[

        ]
    )
    for cart_record in cart_list:
        product = await db.get_product(cart_record["product_id"])
        text = "{} - {} шт."
        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(text=text.format(product["name"], cart_record["number"]),
                                     callback_data=cart_record["id"]),
            ]
        )
    keyboard.inline_keyboard.append(
        [
            InlineKeyboardButton(text="<", callback_data="previous"),
            InlineKeyboardButton(text="Отмена", callback_data="cancel"),
            InlineKeyboardButton(text=">", callback_data="next")
        ]
    )
    return keyboard
