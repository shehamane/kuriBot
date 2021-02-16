from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.db_api.api import db_api as db


async def get_users_list_kb(page_list, page, total):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[

        ]
    )

    for user in page_list:
        kb.inline_keyboard.append(
            [
                InlineKeyboardButton(text=f"{user.id} @{user.username}", callback_data=str(user.id)),
            ]
        )
        kb.inline_keyboard.append(
            [
                InlineKeyboardButton(text="<", callback_data="previous"),
                InlineKeyboardButton(text=f"{page}/{total}", callback_data="page"),
                InlineKeyboardButton(text=">", callback_data="next")
            ])
        kb.inline_keyboard.append(
            [
                InlineKeyboardButton(text="Назад", callback_data="back"),
            ]
        )

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
