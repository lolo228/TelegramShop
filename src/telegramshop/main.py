"""
Главный файл бота
"""
import asyncio
import logging
import os
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from .config import load_config
from .database import Database
from .handlers import get_handlers_router


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Основная функция запуска бота"""
    
    # Загрузка конфигурации
    config = load_config()
    
    if not config.token:
        logger.error("BOT_TOKEN не установлен! Проверьте переменные окружения.")
        return
    
    # Создание директории для базы данных
    db_path = Path(config.database_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Инициализация базы данных
    db = Database(config.database_path)
    await db.init_db()
    logger.info("База данных инициализирована")
    
    # Инициализация дефолтных информационных текстов
    await db.init_default_info_texts()
    logger.info("Информационные тексты инициализированы")
    
    # Инициализация бота и диспетчера
    bot = Bot(
        token=config.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # Регистрация middleware для передачи зависимостей
    @dp.update.outer_middleware()
    async def config_middleware(handler, event, data):
        data["config"] = config
        data["db"] = db
        data["bot"] = bot
        return await handler(event, data)
    
    # Подключение роутеров
    dp.include_router(get_handlers_router())
    
    # Запуск бота
    logger.info("Бот запущен")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


def run():
    """Точка входа для запуска бота"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")


if __name__ == "__main__":
    run()

