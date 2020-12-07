from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

cart_record_watching = InlineKeyboardMarkup(
    inline_keyboard=[
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
