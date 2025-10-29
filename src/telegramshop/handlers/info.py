"""
Обработчики информационных кнопок
"""
from aiogram import Router, F
from aiogram.types import Message

from ..database import Database


router = Router()


@router.message(F.text == "📋 Правила")
async def show_rules(message: Message, db: Database):
    """Показать правила магазина"""
    # Удаляем сообщение пользователя
    try:
        await message.delete()
    except Exception:
        pass
    
    rules_text = await db.get_info_text('rules')
    if not rules_text:
        rules_text = "📋 Правила магазина\n\nТекст правил не установлен администратором."
    await message.answer(rules_text)


@router.message(F.text == "✅ Гарантии")
async def show_guarantees(message: Message, db: Database):
    """Показать гарантии магазина"""
    # Удаляем сообщение пользователя
    try:
        await message.delete()
    except Exception:
        pass
    
    guarantees_text = await db.get_info_text('guarantees')
    if not guarantees_text:
        guarantees_text = "✅ Гарантии\n\nТекст гарантий не установлен администратором."
    await message.answer(guarantees_text)


@router.message(F.text == "❓ Помощь")
async def show_help(message: Message, db: Database):
    """Показать справку"""
    # Удаляем сообщение пользователя
    try:
        await message.delete()
    except Exception:
        pass
    
    help_text = await db.get_info_text('help')
    if not help_text:
        help_text = "❓ Помощь\n\nТекст помощи не установлен администратором."
    await message.answer(help_text)

