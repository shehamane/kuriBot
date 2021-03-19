from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from data.api_config import USERS_PAGE_VOLUME
from filters.is_numeric import IsNumericFilterCallback, IsNumericFilter
from keyboards.default import admin_panel_kb
from keyboards.inline import get_users_list_kb, user_info_kb, get_orders_kb
from states import UserInfo, AdminPanel, Orders

from loader import dp
from utils.db_api.api import db_api as db


@dp.message_handler(Text(ignore_case=True, contains=['пользователи']), state=AdminPanel.AdminPanel)
async def show_users_list(message: Message, state: FSMContext):
    await state.finish()
    await UserInfo.UsersList.set()

    await state.update_data({"page_num": 0})
    await state.update_data({"page_total": int(await db.count_users() / (USERS_PAGE_VOLUME + 1)) + 1})

    text_help = "Для получения информации о пользователе, введите " \
                "его юзернейм или id или выберите из спика."

    await message.answer(text_help, reply_markup=await get_users_list_kb(await db.get_users_list(0), 1,
                                                                         (await state.get_data()).get("page_total")))


@dp.callback_query_handler(state=UserInfo.UsersList, text="back")
async def return_to_admin_panel(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Вы вернулись в панель администратора", reply_markup=admin_panel_kb)
    await AdminPanel.AdminPanel.set()
    return


@dp.callback_query_handler(text="next", state=UserInfo.UsersList)
async def show_next_page(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data["page_num"] < int(await db.count_users() / (USERS_PAGE_VOLUME + 1)):
            data["page_num"] += 1
            await call.message.edit_reply_markup(await get_users_list_kb(await db.get_users_list(data["page_num"]),
                                                                         data["page_num"] + 1, data["page_total"]))


@dp.callback_query_handler(text="previous", state=UserInfo.UsersList)
async def show_previous_page(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data["page_num"] > 0:
            data["page_num"] -= 1
            await call.message.edit_reply_markup(await get_users_list_kb(await db.get_users_list(data["page_num"]),
                                                                         data["page_num"] + 1, data["page_total"]))


@dp.callback_query_handler(IsNumericFilterCallback(), state=UserInfo.UsersList)
async def show_user_info(call: CallbackQuery, state: FSMContext):
    user = await db.get_user(int(call.data))
    await state.update_data({"user_id": user.id})

    text = f"id: {user.id}\n" \
           f"username: {user.username}\n" \
           f"fullname: {user.fullname}\n" \
           f"referral id: {user.referral_id if user.referral_id else 'отсутствует'}"
    await call.message.answer(text, reply_markup=user_info_kb)


@dp.message_handler(IsNumericFilter(), state=UserInfo.UsersList)
async def show_user_info(message: Message, state: FSMContext):
    user = await db.get_user(int(message.text))
    if user:
        await state.update_data({"user_id": user.id})

        text = f"id: {user.id}\n" \
               f"username: {user.username}\n" \
               f"fullname: {user.fullname}\n" \
               f"referral id: {user.referral_id if user.referral_id else 'отсутствует'}"
    else:
        text = "Пользователя с таким id не существует"

    await message.answer(text, reply_markup=user_info_kb)


@dp.message_handler(state=UserInfo.UsersList)
async def show_user_info(message: Message, state: FSMContext):
    username = message.text
    if username[0] == '@':
        username = username[1:]
    user = await db.get_user_by_username(username)
    if user:
        await state.update_data({"user_id": user.id})

        text = f"id: {user.id}\n" \
               f"username: {user.username}\n" \
               f"fullname: {user.fullname}\n" \
               f"referral id: {user.referral_id if user.referral_id else 'отсутствует'}"
    else:
        text = "Пользователя с таким юзернеймом не существует"

    await message.answer(text, reply_markup=user_info_kb)


@dp.callback_query_handler(text="cart", state=UserInfo.UsersList)
async def show_cart(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        cart = await db.get_users_current_cart(data["user_id"])
        cart_items = await db.get_cart_items_by_cart(cart.id)

        text = f"корзина пользователя {data['user_id']}\n\n"
        to_pay = 0

        for record in cart_items:
            product = await db.get_product(record.product_id)
            to_pay += product.price * record.amount
            text += f"{product.name} - {record.amount} | {product.price * record.amount} р.\n"
        text += f"\nСумма: {to_pay} р."

    await call.message.answer(text)


@dp.callback_query_handler(text="history", state=UserInfo.UsersList)
async def show_orders(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        user = await db.get_user(state_data["user_id"])
    await call.message.answer(f"История заказов пользователя {user.username}:",
                              reply_markup=await get_orders_kb(await db.get_orders(user.id)))
    await Orders.OrderList.set()


@dp.callback_query_handler(text="cancel", state=Orders.OrderList)
async def back_to_users_list(call: CallbackQuery, state: FSMContext):
    await show_users_list(call.message, state)
