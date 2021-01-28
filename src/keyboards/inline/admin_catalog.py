from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .catalog import get_subcategories_keyboard


async def get_admin_subcategories_kb(subcategories):
    kb = await get_subcategories_keyboard(subcategories)
    kb.inline_keyboard.pop()
    kb.inline_keyboard.append(
        [
            InlineKeyboardButton(text="+", callback_data="new")
        ]
    )
    kb.inline_keyboard.append(
        [
            InlineKeyboardButton(text="Удалить категорию", callback_data="delete")
        ]
    )
    kb.inline_keyboard.append(
        [
            InlineKeyboardButton(text="Назад", callback_data="back"),
            InlineKeyboardButton(text="Изменить изображение", callback_data="change_image"),
            InlineKeyboardButton(text="Покинуть каталог", callback_data="cancel"),
        ]
    )
    return kb


async def get_admin_products_kb(products, page, total):
    kb = InlineKeyboardMarkup(inline_keyboard=[])

    kb.inline_keyboard.append(
        [
            InlineKeyboardButton(text="+", callback_data="new"),
        ]
    )

    for product in products:
        kb.inline_keyboard.append(
            [
                InlineKeyboardButton(text=product.name, callback_data=product.id)
            ]
        )

    kb.inline_keyboard.append(
        [
            InlineKeyboardButton(text="<", callback_data="previous"),
            InlineKeyboardButton(text=f"{page}/{total}", callback_data="page"),
            InlineKeyboardButton(text=">", callback_data="next"),
        ]
    )

    kb.inline_keyboard.append(
        [
            InlineKeyboardButton(text="Назад", callback_data="back"),
            InlineKeyboardButton(text="Покинуть каталог", callback_data="cancel"),
        ]
    )
    return kb
