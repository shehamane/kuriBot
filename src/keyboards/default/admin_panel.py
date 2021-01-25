from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_panel_kb = ReplyKeyboardMarkup([
    [
        KeyboardButton(text='КАТАЛОГ'),
    ],
    [
        KeyboardButton(text='ПОЛЬЗОВАТЕЛИ'),
    ],
],
    resize_keyboard=True
)
