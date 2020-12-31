import asyncio
import asyncpg
import logging

from gino.schema import GinoSchemaVisitor
from .api import db, db_api, Category

from data.config import PG_HOST, PG_USER, PG_PASS, PG_DBNAME

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)


async def create_db():
    await db.set_bind(f"postgresql://{PG_USER}:{PG_PASS}@{PG_HOST}/kuribot_db")
    db.gino: GinoSchemaVisitor
    # await db.gino.drop_all()
    await db.gino.create_all()

    if not (await db_api.get_category(1)):
        main_category = Category()
        main_category.id = 1
        main_category.name = 'MAIN'
        main_category.is_parent = 1
        await main_category.create()
