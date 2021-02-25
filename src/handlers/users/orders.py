from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, InputFile, InputMediaPhoto

from filters.is_numeric import IsNumericFilterCallback
from keyboards.inline import get_cart_record_watching_kb, get_cart_kb
from utils.misc.files import get_product_image_path
from states import CartListing, Orders

from loader import dp
from utils.db_api.api import db_api as db

from data.api_config import CART_PAGE_VOLUME
from data.media_config import IMG_CART_PATH, IMG_DEFAULT_PATH


@dp.message_handler(Text(contains=['мои заказы'], ignore_case=True))
async def show_orders(message: Message, state: FSMContext):
    await Orders.OrderList.set()
    async with state.proxy() as state_data:
        state_data["main_message"] = await message.answer()
