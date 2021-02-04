from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu_kb = ReplyKeyboardMarkup([
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
