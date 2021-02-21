from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu_kb = ReplyKeyboardMarkup([
    [
        KeyboardButton(text='ОФОРМИТЬ ЗАКАЗ'),
    ],
    [
        KeyboardButton(text='КОРЗИНА'),
        KeyboardButton(text='КАТАЛОГ'),
    ],
    [
        KeyboardButton(text='НАСТРОЙКИ'),
        KeyboardButton(text='ПОМОЩЬ')
    ]
],
    resize_keyboard=True
)
