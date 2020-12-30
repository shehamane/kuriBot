import asyncio
import asyncpg
import logging

from gino.schema import GinoSchemaVisitor
from .new_api import db

from data.config import PG_HOST, PG_USER, PG_PASS, PG_DBNAME

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)


async def create_tables():
    create_db_command = open("create_db.sql", "r").read()

    logging.info("Connecting to database...")
    conn: asyncpg.Connection = await asyncpg.connect(
        user=PG_USER,
        password=PG_PASS,
        host=PG_HOST,
        database=PG_DBNAME
    )
    try:
        await conn.execute(create_db_command)
    except asyncpg.DuplicateTableError:
        logging.info("Table already exists")
    else:
        logging.info("Table has been created")
    await conn.close()


async def create_db():
    await db.set_bind(f"postgresql://{PG_USER}:{PG_PASS}@{PG_HOST}/kuribot_db")
    db.gino: GinoSchemaVisitor
    # await db.gino.drop_all()
    await db.gino.create_all()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_tables())
