from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .catalog import get_subcategories_kb


async def get_admin_subcategories_kb(subcategories):
    kb = await get_subcategories_kb(subcategories)
    kb.inline_keyboard.pop()
    kb.inline_keyboard.append(
        [
            InlineKeyboardButton(text="+", callback_data="new_category")
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

    for product in products:
        kb.inline_keyboard.append(
            [
                InlineKeyboardButton(text=product.name, callback_data=product.id)
            ]
        )

    kb.inline_keyboard.append(
        [
            InlineKeyboardButton(text="+", callback_data="new_product"),
        ]
    )

    kb.inline_keyboard.append(
        [
            InlineKeyboardButton(text="Удалить категорию", callback_data="delete")
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


empty_category_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton("+ ТОВАР", callback_data="new_product"),
            InlineKeyboardButton("+ КАТЕГОРИЯ", callback_data="new_category"),
        ],
        [
            InlineKeyboardButton("Удалить категорию", callback_data="delete"),
            InlineKeyboardButton("Изменить изображение", callback_data="change_image")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back"),
            InlineKeyboardButton(text="Покинуть каталог", callback_data="cancel"),
        ]
    ]
)

download_image_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Добавить изображение товара', callback_data="download_product_image"),
    ],
    [
        InlineKeyboardButton(text='Без изображения', callback_data="without_image")
    ]
])

product_info_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="НАЗВАНИЕ", callback_data="change_name"),
        InlineKeyboardButton(text="ОПИСАНИЕ", callback_data="change_description"),
        InlineKeyboardButton(text="ЦЕНА", callback_data="change_price")
    ],
    [
        InlineKeyboardButton(text="ИЗОБРАЖЕНИЕ", callback_data="change_image"),
        InlineKeyboardButton(text="УДАЛИТЬ", callback_data="delete"),
    ],
    [
        InlineKeyboardButton(text="Назад", callback_data="back")
    ]
])
