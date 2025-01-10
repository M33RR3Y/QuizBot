from dotenv import load_dotenv
import os

# Загружаем переменные окружения из .env файла
load_dotenv()

# Получаем токен из переменной окружения
API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
if not API_TOKEN:
    raise ValueError("API Token not found. Please set TELEGRAM_API_TOKEN in the .env file.")

# Зададим имя базы данных
DB_NAME = 'quiz_bot.db'
