from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

listing_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="<", callback_data="previous"),
            InlineKeyboardButton(text=">", callback_data="next"),
        ],
        [
            InlineKeyboardButton(text="Отмена", callback_data="cancel"),
        ]
    ]
)

product_watching_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Добавить в корзину", callback_data="add_to_cart"),
        ],
        [
            InlineKeyboardButton(text="Вернуться в каталог", callback_data="catalog"),
        ]
    ]
)

return_to_catalog_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Вернуться в каталог", callback_data="catalog"),
        ]
    ]
)


cancel_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Отмена", callback_data="cancel"),
        ]
    ]
)