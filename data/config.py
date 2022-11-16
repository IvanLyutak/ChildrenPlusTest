import os
from dotenv import load_dotenv

load_dotenv()

DRIVER = str(os.getenv("DRIVER"))
BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
DB_PWD = str(os.getenv("DB_PWD"))
DB_UID = str(os.getenv("DB_UID"))
DB_DATABASE = str(os.getenv("DB_DATABASE"))
DB_SERVER = str(os.getenv("DB_SERVER"))

ADMINS_ID = []