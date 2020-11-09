from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu = ReplyKeyboardMarkup([
    [
        KeyboardButton(text='оформить заказ'),
    ],
    [
        KeyboardButton(text='корзина'),
        KeyboardButton(text='каталог'),
    ],
],
    resize_keyboard=True
)
