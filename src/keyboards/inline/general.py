from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

confirmation_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton("Да", callback_data='yes'),
            InlineKeyboardButton("Нет", callback_data='cancel')
         ]
    ]
)

cancel_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton("Отмена", callback_data='cancel')
    ]
])
