from aiogram import types
from gino import Gino
from sqlalchemy import Column, Sequence, BigInteger, String, sql, Integer, Text, Boolean, and_

from data.api_config import CART_PAGE_VOLUME, USERS_PAGE_VOLUME, PRODUCTS_PAGE_VOLUME

db = Gino()


class User(db.Model):
    __tablename__ = "users"
    query: sql.Select

    id = Column(Integer, Sequence("user_id_seq"), primary_key=True)
    user_id = Column(BigInteger, unique=True)
    username = Column(String(30))
    fullname = Column(String(50))
    referral_id = Column(Integer)


class Product(db.Model):
    __tablename__ = "products"
    query: sql.Select

    id = Column(Integer, Sequence("product_id_seq"), primary_key=True)
    name = Column(String(100))
    description = Column(Text)
    price = Column(Integer)
    category_id = Column(Integer)


class Category(db.Model):
    __tablename__ = "categories"
    query: sql.Select

    id = Column(Integer, Sequence("category_id_seq"), primary_key=True)
    name = Column(String(100))
    parent_id = Column(Integer)
    is_parent = Column(Boolean)


class CartRecord(db.Model):
    __tablename__ = "cart"
    query: sql.Select

    id = Column(Integer, Sequence("cart_record_id_seq"), primary_key=True)
    user_id = Column(Integer)
    product_id = Column(Integer)
    amount = Column(Integer)


class DBCommands:
    async def create_user(self, referral=None):
        user = types.User.get_current()

        old_user = await self.get_user_by_chat_id(user.id)
        if old_user:
            return old_user

        new_user = User()
        new_user.user_id = user.id
        new_user.username = user.username
        new_user.fullname = user.full_name
        if referral:
            new_user.referral_id = int(referral)

        await new_user.create()
        return new_user

    async def get_id(self):
        user_id = types.User.get_current().id
        user = await self.get_user_by_chat_id(user_id)
        if not user:
            return None
        return user.id

    async def get_user(self, user_id):
        user = await User.get(user_id)
        return user

    async def count_users(self):
        total = await db.func.count(User.id).gino.scalar()
        return total

    async def get_user_by_chat_id(self, chat_id) -> User:
        user: User = await User.query.where(User.user_id == chat_id).gino.first()
        return user

    async def get_user_by_username(self, username):
        user = await User.query.where(User.username == username).gino.first()
        return user

    async def get_users_list(self, page_num):
        users_list = await User.query.order_by(User.username).limit(USERS_PAGE_VOLUME).offset(
            page_num * USERS_PAGE_VOLUME).gino.all()
        return users_list

    async def get_category(self, category_id):
        category = await Category.get(category_id)
        return category

    async def get_subcategories(self, parent_id):
        categories = await Category.query.where(Category.parent_id == parent_id).gino.all()
        return categories

    async def create_category(self, category_name, parent_id):
        category = Category()
        category.name = category_name
        category.parent_id = parent_id
        category.is_parent = False
        await category.create()

        parent = await self.get_category(parent_id)
        if not parent.is_parent:
            await parent.update(is_parent=True).apply()

        return category

    async def delete_category(self, category_id):
        category = await self.get_category(category_id)

        if category.is_parent:
            subcategories = await self.get_subcategories(category_id)
            for sc in subcategories:
                await self.delete_category(sc.id)
        else:
            products = await self.get_category_products(category_id)
            for product in products:
                await product.delete()

        await category.delete()

    async def get_product_by_page(self, parent_id, page_num):
        product = await Product.query.where(Product.category_id == parent_id).limit(1).offset(page_num).gino.first()
        return product

    async def get_products_by_page(self, parent_id, page_num):
        products = await Product.query.where(Product.category_id == parent_id).limit(PRODUCTS_PAGE_VOLUME).offset(
            page_num * PRODUCTS_PAGE_VOLUME).gino.all()
        return products

    async def create_product(self, name, description, price, category_id):
        product = Product()
        product.name = name
        product.description = description
        product.price = price
        product.category_id = category_id
        await product.create()

        return product.id

    async def delete_product(self, product_id):
        product = await self.get_product(product_id)
        await product.delete()

    async def count_category_products(self, category_id):
        number = await db.select([db.func.count(Product.id)]).where(Product.category_id == category_id).gino.scalar()
        return number

    async def get_category_products(self, category_id):
        products = await Product.query.where(Product.category_id == category_id).gino.all()
        return products

    async def count_subcategories(self, parent_id):
        number = await db.select([db.func.count(Category.id)]).where(Category.parent_id == parent_id).gino.scalar()
        return number

    async def get_product(self, product_id):
        product = await Product.get(product_id)
        return product

    async def get_cart_record(self, record_id):
        cart_record = await CartRecord.get(record_id)
        return cart_record

    async def get_cart_record_by_info(self, product_id):
        user_id = (await self.get_user_by_chat_id(types.User.get_current().id)).id
        cart_record = await CartRecord.query.where(and_(
            CartRecord.user_id == user_id, CartRecord.product_id == product_id)).gino.first()
        return cart_record

    async def add_cart_record(self, product_id, amount):
        cart_record = CartRecord()
        cart_record.user_id = (await self.get_user_by_chat_id(types.User.get_current().id)).id
        cart_record.product_id = product_id
        cart_record.amount = amount
        await cart_record.create()
        return cart_record

    async def change_cart_record(self, product_id, new_amount):
        cart_record = await self.get_cart_record_by_info(product_id)
        await cart_record.update(amount=new_amount).apply()

    async def delete_cart_record(self, product_id):
        cart_record = await self.get_cart_record_by_info(product_id)
        await cart_record.delete()

    async def get_cart_page(self, page_num):
        user_id = (await self.get_user_by_chat_id(types.User.get_current().id)).id
        cart_page = await CartRecord.query.where(CartRecord.user_id == user_id).limit(CART_PAGE_VOLUME).offset(
            page_num * CART_PAGE_VOLUME).gino.all()
        return cart_page

    async def count_cart(self):
        user_id = (await self.get_user_by_chat_id(types.User.get_current().id)).id
        number = await db.select([db.func.count(CartRecord.id)]).where(CartRecord.user_id == user_id).gino.scalar()
        return number

    async def get_cart_by_id(self, user_id):
        cart = await CartRecord.query.where(CartRecord.user_id == user_id).gino.all()
        return cart


db_api = DBCommands()
