"""
Вспомогательные утилиты для бота
"""
import asyncio
from aiogram import Bot
from aiogram.types import Message
from typing import List, Optional


async def delete_message_after_delay(bot: Bot, chat_id: int, message_id: int, delay: int):
    """
    Удалить сообщение через заданное количество секунд
    
    Args:
        bot: Экземпляр бота
        chat_id: ID чата
        message_id: ID сообщения
        delay: Задержка в секундах
    """
    await asyncio.sleep(delay)
    try:
        await bot.delete_message(chat_id, message_id)
    except Exception:
        pass


async def delete_messages(bot: Bot, chat_id: int, message_ids: List[int]):
    """
    Удалить несколько сообщений
    
    Args:
        bot: Экземпляр бота
        chat_id: ID чата
        message_ids: Список ID сообщений для удаления
    """
    for msg_id in message_ids:
        try:
            await bot.delete_message(chat_id, msg_id)
        except Exception:
            pass


async def safe_delete_message(message: Message):
    """
    Безопасное удаление сообщения с обработкой ошибок
    
    Args:
        message: Сообщение для удаления
    """
    try:
        await message.delete()
    except Exception:
        pass

