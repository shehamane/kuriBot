from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

listing = InlineKeyboardMarkup(
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