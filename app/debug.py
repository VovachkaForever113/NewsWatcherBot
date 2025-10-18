import os
from dotenv import load_dotenv

print("Текущая директория:", os.getcwd())
print("Файлы в директории:", os.listdir('.'))

# Пробуем загрузить .env
load_dotenv()

print("BOT_TOKEN из .env:", os.getenv("BOT_TOKEN"))
print("TG_API_ID из .env:", os.getenv("TG_API_ID"))