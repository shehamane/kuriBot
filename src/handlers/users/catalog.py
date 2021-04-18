from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputFile
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from keyboards.inline import get_subcategories_kb, get_product_operating_kb, back_button
from utils.callback_datas import choose_category_cd

from utils.misc.files import get_product_image_path
from utils.db_api.api import db_api as db, Category, Product

from states import Catalog

from data.media_config import IMG_CATALOG_PATH, IMG_DEFAULT_PATH

from loader import dp


@dp.message_handler(Text(ignore_case=True, contains=['каталог']), state='*')
async def show_main_category(message: Message, state: FSMContext):
    await state.finish()
    await state.update_data({"category_id": 1})

    main = await db.get_category(1)
    if await db.is_empty_category(main.id):
        await message.answer("Каталог пуст")
    elif main.is_parent:
        await Catalog.Categories.set()

        answer = await get_category_message(main)
        await message.answer_photo(InputFile(answer["img_path"]), caption=answer["text"], reply_markup=answer["rm"])
    else:
        await Catalog.Product.set()
        page_total = await db.count_products_in_category(main.id)
        first_product = await db.get_product_by_page(main.id, 0)
        await state.update_data({"page_num": 0,
                                 "page_total": page_total,
                                 "amount": 1,
                                 "product_id": first_product.id})

        answer = await get_product_message(first_product, 0, page_total, 1)
        await message.answer_photo(InputFile(answer["img_path"]), caption=answer["text"], reply_markup=answer["rm"])


@dp.callback_query_handler(state=[Catalog.Categories, Catalog.Product], text="back")
async def return_to_parent_category(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data["category_id"] == 1:
            return
        curr_category = await db.get_category(data["category_id"])
        curr_category = await db.get_category(curr_category.parent_id)
        data["category_id"] = curr_category.id

    await Catalog.Categories.set()

    answer = await get_category_message(curr_category)
    await call.message.edit_media(InputMediaPhoto(InputFile(answer["img_path"])))
    await call.message.edit_caption(caption=answer["text"], reply_markup=answer["rm"])


@dp.callback_query_handler(choose_category_cd.filter(), state=Catalog.Categories)
async def show_category(call: CallbackQuery, callback_data: dict, state: FSMContext):
    category_id = int(callback_data.get("category_id"))
    category = await db.get_category(category_id)
    await state.update_data({"category_id": category.id})

    if await db.is_empty_category(category.id):
        await call.message.edit_caption("Категория пуста", reply_markup=back_button)
    elif category.is_parent:
        await Catalog.Categories.set()

        answer = await get_category_message(category)
        await call.message.edit_caption(caption=answer["text"], reply_markup=answer["rm"])
    else:
        await Catalog.Product.set()
        page_total = await db.count_products_in_category(category.id)
        first_product = await db.get_product_by_page(category.id, 0)
        await state.update_data({"page_num": 0,
                                 "page_total": page_total,
                                 "amount": 1,
                                 "product_id": first_product.id})

        answer = await get_product_message(first_product, 0, page_total, 1)
        await call.message.edit_media(InputMediaPhoto(InputFile(answer["img_path"])))
        await call.message.edit_caption(caption=answer["text"], reply_markup=answer["rm"])


@dp.callback_query_handler(state=Catalog.Product, text="next")
async def show_next_product(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["amount"] = 1
        data["page_num"] = (data["page_num"] + 1) % data["page_total"]
        next_product = await db.get_product_by_page(data["category_id"],
                                                    data["page_num"])
        data["product_id"] = next_product.id

        answer = await get_product_message(next_product, data["page_num"], data["page_total"], data["amount"])
        await call.message.edit_media(InputMediaPhoto(InputFile(answer["img_path"])))
        await call.message.edit_caption(caption=answer["text"], reply_markup=answer["rm"])


@dp.callback_query_handler(state=Catalog.Product, text="previous")
async def show_previous_product(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["amount"] = 1
        data["page_num"] -= 1
        if data["page_num"] == -1:
            data["page_num"] += data["page_total"]
        previous_product = await db.get_product_by_page(data["category_id"],
                                                        data["page_num"])
        data["product_id"] = previous_product.id

        answer = await get_product_message(previous_product, data["page_num"], data["page_total"], data["amount"])
        await call.message.edit_media(InputMediaPhoto(InputFile(answer["img_path"])))
        await call.message.edit_caption(caption=answer["text"], reply_markup=answer["rm"])


@dp.callback_query_handler(state=Catalog.Product, text="increase")
async def increase_amount(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["amount"] += 1

        await call.message.edit_reply_markup(await get_product_operating_kb(data["page_num"],
                                                                            data["page_total"],
                                                                            data["amount"]))


@dp.callback_query_handler(state=Catalog.Product, text="decrease")
async def decrease_amount(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data["amount"] == 1:
            return
        data["amount"] -= 1

        await call.message.edit_reply_markup(await get_product_operating_kb(data["page_num"],
                                                                            data["page_total"],
                                                                            data["amount"]))


@dp.callback_query_handler(state=Catalog.Product, text="add_to_cart")
async def add_to_cart(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        cart_item = await db.get_cart_item_by_user(data["product_id"])

        if not cart_item:
            await db.create_cart_item(data["product_id"], data["amount"])
        else:
            await db.change_cart_item_amount(cart_item.id,
                                             cart_item.amount + data["amount"])

        await call.message.edit_caption(call.message.caption + "\n Товар добавлен в корзину!",
                                        reply_markup=await get_product_operating_kb(data["page_num"],
                                                                                    data["page_total"],
                                                                                    data["amount"]))


async def get_category_message(category: Category):
    message = {"text": category.name,
               "rm": await get_subcategories_kb(await db.get_subcategories(category.id)),
               "img_path": IMG_CATALOG_PATH}
    return message


async def get_product_message(product: Product, page_num, page_total, amount):
    text = f'{product.name}\n' \
           f'{product.description}\n' \
           f'Цена: {product.price} р.'
    message = {"text": text,
               "rm": await get_product_operating_kb(page_num, page_total, amount),
               "img_path": await get_product_image_path(product.id) or IMG_DEFAULT_PATH}
    return message
