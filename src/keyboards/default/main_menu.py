from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu_kb = ReplyKeyboardMarkup([
    [
        KeyboardButton(text='ОФОРМИТЬ ЗАКАЗ'),
    ],
    [
        KeyboardButton(text='КАТАЛОГ')
    ],
    [
        KeyboardButton(text='КОРЗИНА'),
        KeyboardButton(text='МОИ ЗАКАЗЫ'),
    ],
    [
        KeyboardButton(text='НАСТРОЙКИ'),
        KeyboardButton(text='ПОМОЩЬ')
    ]
],
    resize_keyboard=True
)
