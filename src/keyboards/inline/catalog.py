from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.callback_datas import choose_category_cd
from utils.db_api.api import Category


async def get_product_operating_kb(page, total, amount):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="-", callback_data="decrease"),
                InlineKeyboardButton(text="+", callback_data="increase"),
                InlineKeyboardButton(text=str(amount), callback_data="amount"),
            ],
            [
                InlineKeyboardButton(text="Добавить в корзину", callback_data="add_to_cart"),
            ],
            [
                InlineKeyboardButton(text="<", callback_data="previous"),
                InlineKeyboardButton(text=f"{page + 1}/{total}", callback_data="page"),
                InlineKeyboardButton(text=">", callback_data="next"),
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data="back"),
            ]
        ]
    )


async def get_subcategories_kb(subcategories: [Category]):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for subcategory in subcategories:
        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(text=f'{subcategory.name}',
                                     callback_data=choose_category_cd.new(category_id=subcategory.id))
            ]
        )
    keyboard.inline_keyboard.append(
        [
            InlineKeyboardButton(text="Назад", callback_data="back"),
        ]
    )
    return keyboard
