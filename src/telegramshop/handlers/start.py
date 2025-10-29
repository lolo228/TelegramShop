"""
Обработчики команды /start и проверки подписки
"""
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from ..config import BotConfig
from ..database import Database
from ..keyboards import get_subscription_keyboard, get_main_keyboard


router = Router()


async def check_user_subscription(bot, user_id: int, channel_id: str) -> bool:
    """Проверка подписки пользователя на канал"""
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except TelegramBadRequest:
        return False


@router.message(CommandStart())
async def cmd_start(message: Message, config: BotConfig, db: Database, bot):
    """Обработчик команды /start"""
    user = message.from_user
    
    # Добавляем пользователя в базу данных
    await db.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name
    )
    
    # Проверяем, не заблокирован ли пользователь
    user_data = await db.get_user(user.id)
    if user_data and user_data.get('is_blocked'):
        await message.answer(
            "🚫 Ваш аккаунт заблокирован.\n"
            "Для получения дополнительной информации обратитесь к администратору."
        )
        return
    
    # Проверяем, нужна ли проверка подписки
    if config.check_subscription and config.channel_id:
        is_subscribed = await check_user_subscription(bot, user.id, config.channel_id)
        
        if not is_subscribed:
            await message.answer(
                "❄️ Для того, чтобы пользоваться ботом и получать бесплатные раздачи, "
                "перейдите по кнопке и подпишитесь на канал!\n\n"
                "В канале публикуем раздачи и халяву Steam",
                reply_markup=get_subscription_keyboard(config.channel_url or config.channel_id)
            )
            return
    
    # Если подписка не требуется или пользователь подписан
    await message.answer(
        "❄️ Добро пожаловать! Воспользуйтесь меню для покупки товаров",
        reply_markup=get_main_keyboard()
    )


@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery, config: BotConfig, bot):
    """Обработчик проверки подписки"""
    user_id = callback.from_user.id
    
    if not config.check_subscription or not config.channel_id:
        await callback.message.edit_text(
            "❄️ Добро пожаловать! Воспользуйтесь меню для покупки товаров"
        )
        await callback.message.answer(
            "Выберите действие:",
            reply_markup=get_main_keyboard()
        )
        await callback.answer()
        return
    
    is_subscribed = await check_user_subscription(bot, user_id, config.channel_id)
    
    if is_subscribed:
        await callback.message.edit_text(
            "❄️ Добро пожаловать! Воспользуйтесь меню для покупки товаров"
        )
        await callback.message.answer(
            "Выберите действие:",
            reply_markup=get_main_keyboard()
        )
        await callback.answer("✅ Подписка подтверждена!")
    else:
        await callback.answer(
            "❌ Вы не подписаны на канал! Пожалуйста, подпишитесь и попробуйте снова.",
            show_alert=True
        )

