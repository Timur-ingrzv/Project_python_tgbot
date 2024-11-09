import logging
from dotenv import load_dotenv
import os

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

load_dotenv()
TOKEN = str(os.getenv('BOT_TOKEN'))
PASSWORD_DB = str(os.getenv('PASSWORD_DB'))
TOKEN_YANDEX = str(os.getenv(''))


DATABASE_CONFIG = {
    "database": "tgbot_for_study",
    "user": "postgres",
    "password": PASSWORD_DB,
    "host": "localhost",
    "port": "5432",
}
