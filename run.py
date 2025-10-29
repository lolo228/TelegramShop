"""
Скрипт для запуска бота
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Загрузка переменных окружения из .env
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Запуск бота
from src.telegramshop.main import run

if __name__ == "__main__":
    run()

