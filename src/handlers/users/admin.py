from aiogram.types import Message
from aiogram.dispatcher.filters import Command, Text
from aiogram.dispatcher import FSMContext
from re import match

from utils.misc.files import download_product_image

from utils.db_api.api import db
from loader import dp

from states.product_addition import ProductAddition
from states.product_removing import ProductRemoving


@dp.message_handler(Command("new_product"), state=None)
async def add_product(message: Message):
    await message.answer("Введите имя нового продукта: ")

    await ProductAddition.NameRequest.set()


@dp.message_handler(state=ProductAddition.NameRequest)
async def get_addition_name(message: Message, state: FSMContext):
    name = message.text
    if name.isnumeric():
        await message.answer(f"Имя товара не может состоять только из цифр! Попробуйте еще раз:")
        return
    await state.update_data({"name": name})

    await message.answer(f"Добавьте описание для {name}:")
    await ProductAddition.next()


@dp.message_handler(state=ProductAddition.DescriptionRequest)
async def get_description(message: Message, state: FSMContext):
    description = message.text
    await state.update_data({"description": description})

    name = (await state.get_data()).get("name")
    id = await db.add_new_product(name, description)
    await state.update_data({"id": id})

    await message.answer(f"Добавьте изображение для {name} (или отправьте любое сообщение чтобы пропустить):")
    await ProductAddition.next()


@dp.message_handler(state=ProductAddition.ImageRequest, content_types=['photo'])
async def get_image(message: Message, state: FSMContext):
    product_id = (await state.get_data()).get("id")
    await download_product_image(product_id, message.photo[-1])
    await message.answer(f"Продукт успешно добавлен!")
    await state.finish()


@dp.message_handler(state=ProductAddition.ImageRequest)
async def add_product_final(message: Message, state: FSMContext):
    await message.answer(f"Продукт успешно добавлен!")
    await state.finish()


######################################################################

@dp.message_handler(Command("remove_product"), state=None)
async def remove_product(message: Message):
    await message.answer("Введите имя или ID продукта, который хотите удалить:")

    await ProductRemoving.NameRequest.set()


@dp.message_handler(state=ProductRemoving.NameRequest)
async def get_removing_name(message: Message, state: FSMContext):
    text = message.text
    if text.isnumeric():
        await db.remove_product(int(text))
    else:
        await db.remove_product_by_name(text)

    await message.answer("Продукт успешно удален!")
    await state.finish()
