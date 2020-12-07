from aiogram import types
from asyncpg import Connection, Record
from asyncpg.exceptions import UniqueViolationError

from loader import db_pool


class DBCommands:
    pool: Connection = db_pool
    ADD_NEW_USER = "INSERT INTO users(chat_id, username, full_name) VALUES ($1, $2, $3) RETURNING id"
    COUNT_USERS = "SELECT COUNT(*) FROM users"
    GET_ID = "SELECT id FROM users WHERE chat_id = $1"
    CHANGE_FULLNAME = "UPDATE users SET full_name = $2 WHERE chat_id = $1"

    ADD_NEW_PRODUCT = "INSERT INTO products(name, description) VALUES ($1, $2) RETURNING id"
    REMOVE_PRODUCT_BY_NAME = "DELETE FROM products WHERE name = $1"
    REMOVE_PRODUCT = "DELETE FROM products WHERE id = $1"
    GET_PRODUCTS_LIST = "SELECT id, name FROM products OFFSET $1 LIMIT $2"
    COUNT_PRODUCTS = "SELECT COUNT(*) FROM products"
    GET_PRODUCT = "SELECT name, description FROM products WHERE id = $1"

    ADD_TO_CART = "INSERT INTO cart(user_id, product_id, number) VALUES  ($1, $2, $3) RETURNING id"
    CHANGE_FROM_CART = "UPDATE cart SET number=$3 WHERE user_id = $1 AND product_id = $2"
    DELETE_FROM_CART = "DELETE FROM cart WHERE user_id = $1 AND product_id = $2"
    GET_CART_LIST = "SELECT id, product_id, number FROM cart WHERE user_id = $1 OFFSET $2 LIMIT $3"
    COUNT_CART = "SELECT COUNT(*) FROM cart WHERE user_id = $1"
    GET_CART_RECORD = "SELECT product_id, number FROM cart WHERE id = $1"
    GET_CART_RECORD_BY_PRODUCT = "SELECT id, number FROM cart WHERE user_id = $1 AND product_id = $2"

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

    async def remove_product_by_name(self, name):
        command = self.REMOVE_PRODUCT_BY_NAME
        return await self.pool.execute(command, name)

    async def remove_product(self, product_id):
        command = self.REMOVE_PRODUCT
        return await self.pool.execute(command, product_id)

    async def get_products_list(self, offset, limit):
        command = self.GET_PRODUCTS_LIST
        return await self.pool.fetch(command, offset, limit)

    async def count_products(self):
        command = self.COUNT_PRODUCTS
        return await self.pool.fetchval(command)

    async def get_product(self, product_id):
        command = self.GET_PRODUCT
        return await self.pool.fetchrow(command, product_id)

    async def add_to_cart(self, product_id, number):
        command = self.ADD_TO_CART
        user_id = await self.get_id()
        return await self.pool.fetchval(command, user_id, product_id, number)

    async def change_from_cart(self, product_id, new_number):
        command = self.CHANGE_FROM_CART
        user_id = await self.get_id()
        return await self.pool.fetchval(command, user_id, product_id, new_number)

    async def delete_from_cart(self, product_id):
        command = self.DELETE_FROM_CART
        user_id = await self.get_id()
        return await self.pool.fetchval(command, user_id, product_id)

    async def get_cart_list(self, offset, limit):
        command = self.GET_CART_LIST
        user_id = await self.get_id()
        return await self.pool.fetch(command, user_id, offset, limit)

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


db = DBCommands()
