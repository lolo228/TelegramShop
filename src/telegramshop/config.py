"""
Конфигурация бота
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class BotConfig:
    """Конфигурация бота"""
    token: str
    admin_ids: list[int]
    
    # Настройки канала для обязательной подписки
    channel_id: Optional[str] = None  # Например: @channelname или -100123456789
    channel_url: Optional[str] = None  # Ссылка на канал
    check_subscription: bool = False  # Включить/выключить проверку подписки
    
    # База данных
    database_path: str = "data/shop.db"


def load_config() -> BotConfig:
    """Загрузка конфигурации из переменных окружения"""
    
    # Получаем список админов из строки, разделённой запятыми
    admin_ids_str = os.getenv("ADMIN_IDS", "")
    admin_ids = [int(id.strip()) for id in admin_ids_str.split(",") if id.strip()]
    
    return BotConfig(
        token=os.getenv("BOT_TOKEN", ""),
        admin_ids=admin_ids,
        channel_id=os.getenv("CHANNEL_ID"),
        channel_url=os.getenv("CHANNEL_URL"),
        check_subscription=os.getenv("CHECK_SUBSCRIPTION", "false").lower() == "true",
        database_path=os.getenv("DATABASE_PATH", "data/shop.db"),
    )

