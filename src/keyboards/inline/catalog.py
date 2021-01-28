from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def get_product_watching_kb(page, total, amount):
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
                InlineKeyboardButton(text=f"{page}/{total}", callback_data="page"),
                InlineKeyboardButton(text=">", callback_data="next"),
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data="back"),
                InlineKeyboardButton(text="Покинуть каталог", callback_data="cancel")
            ]
        ]
    )


return_to_catalog_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Вернуться в каталог", callback_data="catalog"),
        ]
    ]
)

cancel_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Отмена", callback_data="cancel"),
        ]
    ]
)


async def get_subcategories_keyboard(subcategories):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    for subcategory in subcategories:
        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(text=f'{subcategory.name}',
                                     callback_data=subcategory.id)
            ]
        )
    keyboard.inline_keyboard.append(
        [
            InlineKeyboardButton(text="Назад", callback_data="back"),
            InlineKeyboardButton(text="Покинуть каталог", callback_data="cancel"),
        ]
    )
    return keyboard
