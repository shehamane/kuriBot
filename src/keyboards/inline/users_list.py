from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.callback_datas import choose_user_cd
from utils.db_api.api import db_api as db


async def get_users_list_kb(page_list, page, total):
    kb = InlineKeyboardMarkup()

    for user in page_list:
        kb.inline_keyboard.append(
            [
                InlineKeyboardButton(text=f"{user.id} @{user.username}",
                                     callback_data=choose_user_cd.new(user_id=user.id)),
            ]
        )
    kb.inline_keyboard.append(
        [
            InlineKeyboardButton(text="<", callback_data="previous"),
            InlineKeyboardButton(text=f"{page}/{total}", callback_data="page"),
            InlineKeyboardButton(text=">", callback_data="next")
        ])

    return kb


user_info_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Посмотреть корзину", callback_data="cart"),
        ],
        [
            InlineKeyboardButton(text="Посмотреть историю заказов", callback_data="history"),
        ]
    ]
)
