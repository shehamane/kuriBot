from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

register_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton("Зарегестрирваться", callback_data="register")
    ]
])

registration_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton("Имя", callback_data="name")
    ],
    [
        InlineKeyboardButton("Телефон", callback_data="phone_number")
    ],
    [
        InlineKeyboardButton("Адрес доставки", callback_data="address")
    ],
    [
        InlineKeyboardButton("Завершить", callback_data="finish")
    ]
])
