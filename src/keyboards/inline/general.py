from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def add_button(kb: InlineKeyboardMarkup, button: InlineKeyboardButton):
    kb.inline_keyboard.append([button])
    return kb


start_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton("Старт", callback_data="start")
        ]
    ]
)

confirmation_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton("Да", callback_data='yes'),
            InlineKeyboardButton("Нет", callback_data='no')
        ]
    ]
)
confirmation_cancel_kb = InlineKeyboardMarkup(
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

back_button = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton("Назад", callback_data="back")
    ]
])
