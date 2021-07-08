from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.callback_datas import choose_delivery_method_cd
from utils.db_api.api import DeliveryMetod


async def get_delivery_kb(methods: [DeliveryMetod]):
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for method in methods:
        kb.inline_keyboard.append([
            InlineKeyboardButton(text=f'{method.name}',
                                 callback_data=choose_delivery_method_cd.new(method_id=method.id))
        ])
    kb.inline_keyboard.append([InlineKeyboardButton(text="+", callback_data="new_method")])
    return kb
