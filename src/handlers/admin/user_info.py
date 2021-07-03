from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from data.api_config import USERS_PAGE_VOLUME
from filters.is_numeric import IsNumericFilter
from keyboards.default import admin_panel_kb
from keyboards.default.admin_panel import back_kb
from keyboards.inline import get_users_list_kb, user_info_kb, get_orders_kb
from states import UserInfo, AdminPanel, AdminCatalog
from utils.callback_datas import choose_user_cd, choose_order_cd

from loader import dp
from utils.db_api.api import db_api as db


@dp.message_handler(Text(ignore_case=True, contains=['пользователи']),
                    state=[AdminPanel.AdminPanel, AdminCatalog.Categories, AdminCatalog.Products,
                           AdminCatalog.EmptyCategory, AdminCatalog.ProductInfo])
async def show_users_list(message: Message, state: FSMContext):
    await state.finish()
    await UserInfo.UsersList.set()

    await message.answer("Список пользователей", reply_markup=back_kb)

    await state.update_data({"page_num": 0})
    await state.update_data({"page_total": int(await db.count_users() / (USERS_PAGE_VOLUME + 1)) + 1})

    text_help = "Для получения информации о пользователе, введите " \
                "его юзернейм или id или выберите из спика."

    await message.answer(text_help, reply_markup=await get_users_list_kb(await db.get_users_list(0), 1,
                                                                         (await state.get_data()).get("page_total")))


@dp.message_handler(Text(contains="отмена", ignore_case=True), state=UserInfo.all_states)
async def back_to_admin_panel(message: Message, state: FSMContext):
    await message.answer("Вы вернулись в панель администратора.", reply_markup=admin_panel_kb)
    await state.finish()
    await AdminPanel.AdminPanel.set()


@dp.message_handler(Text(equals="НАЗАД"), state=UserInfo.all_states)
async def return_to_admin_panel(message: Message, state: FSMContext):
    await message.answer("Вы вернулись в панель администратора", reply_markup=admin_panel_kb)
    await state.finish()
    await AdminPanel.AdminPanel.set()


@dp.callback_query_handler(text="next", state=UserInfo.all_states)
async def show_next_page(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data["page_num"] < int(await db.count_users() / (USERS_PAGE_VOLUME + 1)):
            data["page_num"] += 1
            await call.message.edit_reply_markup(await get_users_list_kb(await db.get_users_list(data["page_num"]),
                                                                         data["page_num"] + 1, data["page_total"]))


@dp.callback_query_handler(text="previous", state=UserInfo.all_states)
async def show_previous_page(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data["page_num"] > 0:
            data["page_num"] -= 1
            await call.message.edit_reply_markup(await get_users_list_kb(await db.get_users_list(data["page_num"]),
                                                                         data["page_num"] + 1, data["page_total"]))


@dp.callback_query_handler(choose_user_cd.filter(), state=UserInfo.all_states)
async def show_user_info(call: CallbackQuery, callback_data: dict, state: FSMContext):
    user = await db.get_user(int(callback_data.get("user_id")))
    await state.update_data({"user_id": user.id})

    text = f"id: {user.id}\n" \
           f"username: {user.username}\n" \
           f"referral id: {user.referral_id if user.referral_id else 'отсутствует'}"
    await call.message.answer(text, reply_markup=user_info_kb)


@dp.message_handler(IsNumericFilter(), state=UserInfo.all_states)
async def show_user_info(message: Message, state: FSMContext):
    user = await db.get_user(int(message.text))
    if user:
        await state.update_data({"user_id": user.id})

        text = f"id: {user.id}\n" \
               f"username: {user.username}\n" \
               f"referral id: {user.referral_id if user.referral_id else 'отсутствует'}"
        await message.answer(text, reply_markup=user_info_kb)
    else:
        await message.answer("Пользователя с таким id не существует")


@dp.message_handler(state=UserInfo.all_states)
async def show_user_info(message: Message, state: FSMContext):
    username = message.text
    if username[0] == '@':
        username = username[1:]
    user = await db.get_user_by_username(username)
    if user:
        await state.update_data({"user_id": user.id})

        text = f"id: {user.id}\n" \
               f"username: {user.username}\n" \
               f"referral id: {user.referral_id if user.referral_id else 'отсутствует'}"
        await message.answer(text, reply_markup=user_info_kb)

    else:
        await message.answer("Пользователя с таким юзернеймом не существует")


@dp.callback_query_handler(text="cart", state=UserInfo.all_states)
async def show_cart(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        cart_items = await db.get_cart_items_by_user(data["user_id"])

        text = f"Корзина пользователя id{data['user_id']}:\n\n"
        to_pay = 0

        for record in cart_items:
            product = await db.get_product(record.product_id)
            to_pay += product.price * record.amount
            text += f"{product.name} - {record.amount} | {product.price * record.amount} р.\n"
        text += f"\nСумма: {to_pay} р."

    await call.message.answer(text)


@dp.callback_query_handler(text="history", state=UserInfo.all_states)
async def show_orders(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        user = await db.get_user(state_data["user_id"])
        state_data["username"] = user.username
    await call.message.answer(f"История заказов пользователя {user.username}:",
                              reply_markup=await get_orders_kb(await db.get_orders(user.id)))
    await UserInfo.OrdersList.set()


@dp.callback_query_handler(choose_order_cd.filter(), state=UserInfo.all_states)
async def show_order_info(call: CallbackQuery, callback_data: dict):
    await UserInfo.OrderInfo.set()

    order = await db.get_order(int(callback_data["order_id"]))
    cart_items = await db.get_cart_items_by_cart(order.cart_id)

    text = f"ЗАКАЗ ОТ {order.date}\n\n"
    for cart_item in cart_items:
        product = await db.get_product(cart_item.product_id)
        text += f"{product.name} x {cart_item.amount} \t\t\t\t\t {product.price * cart_item.amount}р.\n"
    text += f"\nСумма: {order.price}р.\n"

    await call.message.answer(text)
