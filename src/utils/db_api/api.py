from aiogram import types
from asyncpg import Connection, Record
from asyncpg.exceptions import UniqueViolationError

from data.api_config import PAGE_VOLUME

from loader import db_pool


class DBCommands:
    pool: Connection = db_pool
    ADD_NEW_USER = "INSERT INTO users(chat_id, username, full_name) VALUES ($1, $2, $3) RETURNING id"
    COUNT_USERS = "SELECT COUNT(*) FROM users"
    GET_ID = "SELECT id FROM users WHERE chat_id = $1"
    CHANGE_FULLNAME = "UPDATE users SET full_name = $2 WHERE chat_id = $1"

    ADD_NEW_CATEGORY = "INSERT INTO categories(name, parent_id, is_parent) VALUES ($1, $2, $3) RETURNING id"
    GET_SUBCATEGORIES = "SELECT id, name, is_parent FROM categories WHERE parent_id=$1"
    GET_CATEGORY = "SELECT name, parent_id, is_parent, products_number FROM categories_info WHERE id=$1"
    GET_PRODUCT_BY_NUMBER = "SELECT id, name, description, price FROM products WHERE category_id=$1 OFFSET $2 LIMIT 1"
    COUNT_CATEGORY_PRODUCTS = "SELECT COUNT(*) FROM products WHERE category_id=$1"

    ADD_NEW_PRODUCT = "INSERT INTO products(name, description) VALUES ($1, $2) RETURNING id"
    REMOVE_PRODUCT = "DELETE FROM products WHERE id = $1"
    COUNT_PRODUCTS = "SELECT COUNT(*) FROM products"
    GET_PRODUCT = "SELECT name, description, price FROM products WHERE id = $1"

    ADD_TO_CART = "INSERT INTO cart(user_id, product_id, amount) VALUES  ($1, $2, $3) RETURNING id"
    CHANGE_FROM_CART = "UPDATE cart SET amount=$3 WHERE user_id = $1 AND product_id = $2"
    DELETE_FROM_CART = "DELETE FROM cart WHERE user_id = $1 AND product_id = $2"
    GET_CART_LIST = "SELECT id, product_id, amount FROM cart WHERE user_id = $1 OFFSET $2 LIMIT $3"
    COUNT_CART = "SELECT COUNT(*) FROM cart WHERE user_id = $1"
    GET_CART_RECORD = "SELECT product_id, amount FROM cart WHERE id = $1"
    GET_CART_RECORD_BY_PRODUCT = "SELECT id, amount FROM cart WHERE user_id = $1 AND product_id = $2"

    async def add_new_user(self):
        user = types.User.get_current()

        chat_id = user.id
        username = user.username
        full_name = user.full_name
        args = chat_id, username, full_name

        command = self.ADD_NEW_USER

        try:
            record_id = await self.pool.fetchval(command, *args)
            return record_id
        except UniqueViolationError:
            pass

    async def count_users(self):
        record: Record = await self.pool.fetchval(self.COUNT_USERS)
        return record

    async def get_id(self):
        command = self.GET_ID
        user_id = types.User.get_current().id
        return await self.pool.fetchval(command, user_id)

    async def change_fullname(self, fullname: str):
        command = self.CHANGE_FULLNAME
        user_id = types.User.get_current().id
        await self.pool.execute(command, user_id, fullname)

    async def add_new_product(self, name, description):
        command = self.ADD_NEW_PRODUCT
        return await self.pool.fetchval(command, name, description)

    async def remove_product(self, product_id):
        command = self.REMOVE_PRODUCT
        return await self.pool.execute(command, product_id)

    async def get_product_by_number(self, category_id, number):
        command = self.GET_PRODUCT_BY_NUMBER
        return await self.pool.fetchrow(command, category_id, number)

    async def count_products(self):
        command = self.COUNT_PRODUCTS
        return await self.pool.fetchval(command)

    async def get_product(self, product_id):
        command = self.GET_PRODUCT
        return await self.pool.fetchrow(command, product_id)

    async def add_to_cart(self, product_id, amount):
        command = self.ADD_TO_CART
        user_id = await self.get_id()
        return await self.pool.fetchval(command, user_id, product_id, amount)

    async def change_from_cart(self, product_id, new_amount):
        command = self.CHANGE_FROM_CART
        user_id = await self.get_id()
        return await self.pool.fetchval(command, user_id, product_id, new_amount)

    async def delete_from_cart(self, product_id):
        command = self.DELETE_FROM_CART
        user_id = await self.get_id()
        return await self.pool.fetchval(command, user_id, product_id)

    async def get_cart_list(self, page_num):
        command = self.GET_CART_LIST
        user_id = await self.get_id()
        return await self.pool.fetch(command, user_id, page_num*PAGE_VOLUME, PAGE_VOLUME)

    async def count_cart(self):
        command = self.COUNT_CART
        user_id = await self.get_id()
        return await self.pool.fetchval(command, user_id)

    async def get_cart_record(self, record_id):
        command = self.GET_CART_RECORD
        return await self.pool.fetchrow(command, record_id)

    async def get_cart_record_by_product(self, product_id):
        command = self.GET_CART_RECORD_BY_PRODUCT
        user_id = await self.get_id()
        return await self.pool.fetchrow(command, user_id, product_id)

    async def add_new_category(self, name, parent_id, is_parent):
        command = self.ADD_NEW_CATEGORY
        return await self.pool.fetchval(command, name, parent_id, is_parent)

    async def get_subcategories(self, parent_id):
        command = self.GET_SUBCATEGORIES
        return await self.pool.fetch(command, parent_id)

    async def get_category(self, category_id):
        command = self.GET_CATEGORY
        return await self.pool.fetchrow(command, category_id)

    async def count_category_products(self, category_id):
        command = self.COUNT_CATEGORY_PRODUCTS
        return await self.pool.fetchval(command, category_id)


db = DBCommands()
