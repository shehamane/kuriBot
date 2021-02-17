from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from keyboards.default import main_menu_kb
from loader import dp


@dp.message_handler(Text(equals="отмена", ignore_case=True), state='*')
async def cancel(message: Message, state: FSMContext):
    await message.answer("Вы покинули раздел", reply_markup=main_menu_kb)
    await state.finish()


@dp.callback_query_handler(text="cancel", state='*')
async def cancel(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=0)
    await call.message.answer("Вы покинули раздел", reply_markup=main_menu_kb)
    await state.finish()