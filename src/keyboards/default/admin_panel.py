from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_panel_kb = ReplyKeyboardMarkup([
    [
        KeyboardButton(text='КАТАЛОГ'),
    ],
    [
        KeyboardButton(text='ПОЛЬЗОВАТЕЛИ'),
    ],
    [
        KeyboardButton(text="НАСТРОЙКИ"),
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

settings_kb = ReplyKeyboardMarkup([
    [
        KeyboardButton(text="Внешний вид")
    ],
    [
        KeyboardButton(text="Оплата")
    ],
    [
        KeyboardButton(text="Назад"),
    ]
])

appearance_settings_kb = ReplyKeyboardMarkup([
    [
        KeyboardButton(text="Изображение каталога")
    ],
    [
        KeyboardButton(text="Изображение корзины")
    ],
    [
        KeyboardButton(text="Назад"),
    ]
])

payment_settings_kb = ReplyKeyboardMarkup([
    [
        KeyboardButton(text="Валюта")
    ],
    [
        KeyboardButton(text="Способы доставки")
    ],
    [
        KeyboardButton(text="Способы оплаты")
    ],
    [
        KeyboardButton(text="Назад")
    ]
])
