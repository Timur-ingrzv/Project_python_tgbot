import logging
from dotenv import load_dotenv
import os
from cryptography.fernet import Fernet

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

load_dotenv()
BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
PASSWORD_DB = str(os.getenv("PASSWORD_DB"))
YANDEX_TOKEN = str(os.getenv("YANDEX_TOKEN"))
KEY_HASH = str(os.getenv("KEY_HASH"))

hasher = Fernet(KEY_HASH)

DATABASE_CONFIG = {
    "database": "tgbot_for_study",
    "user": "postgres",
    "password": PASSWORD_DB,
    "host": "localhost",
    "port": "5432",
}
