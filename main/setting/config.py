import os

from dotenv import find_dotenv, load_dotenv
from loguru import logger

logger.add("file.log", format="{name} {message}")

if not find_dotenv():
    exit("Переменные окружения не загружены, так как отсутствует файл .env")
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
super_admins = (
    int(os.environ["TANYA_ID"]),
    int(os.environ["DINARA_ID"]),
    int(os.environ['VOVA_ID'])
)


