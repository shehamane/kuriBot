import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
PAYMENT_TOKEN = str(os.getenv("TRANZO_TOKEN"))
ADMIN_ID = os.getenv("ADMIN_ID")
PG_HOST = os.getenv("PG_HOST")
PG_USER = os.getenv("PG_USER")
PG_PASS = os.getenv("PG_PASS")
PG_DBNAME = os.getenv("PG_DBNAME")
