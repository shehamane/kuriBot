from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

payment_method_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Оплата картой через Telegram", callback_data="tlg")],
    [InlineKeyboardButton(text="Оплата переводом", callback_data="trf")],
    [InlineKeyboardButton(text="Оплата наличными курьеру", callback_data="csh")],
    [InlineKeyboardButton(text="Другое...", callback_data="spc")]
])
