from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_panel_kb = ReplyKeyboardMarkup([
    [
        KeyboardButton(text='КАТАЛОГ'),
    ],
    [
        KeyboardButton(text='ПОЛЬЗОВАТЕЛИ'),
    ],
    [
        KeyboardButton(text='ОТМЕНА'),
    ]
],
    resize_keyboard=True
)

back_kb = ReplyKeyboardMarkup([
    [
        KeyboardButton(text="НАЗАД"),
    ]
], resize_keyboard=True)
