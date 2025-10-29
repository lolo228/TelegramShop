"""
Обработчики профиля пользователя
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from datetime import datetime

from ..database import Database
from ..keyboards import get_profile_keyboard, get_back_keyboard


router = Router()


@router.message(F.text == "👤 Профиль")
async def show_profile(message: Message, db: Database):
    """Показать профиль пользователя"""
    # Удаляем сообщение пользователя
    try:
        await message.delete()
    except Exception:
        pass
    
    user_id = message.from_user.id
    user_data = await db.get_user(user_id)
    
    if not user_data:
        await message.answer("❌ Произошла ошибка. Попробуйте /start")
        return
    
    username = f"@{message.from_user.username}" if message.from_user.username else "Не указан"
    
    profile_text = (
        f"❤️ Пользователь: {username}\n"
        f"💸 Количество покупок: {user_data['purchases_count']}\n"
        f"💰 Ваш баланс: {user_data['balance']:.2f} ₽\n"
        f"🔑 ID: {user_id}"
    )
    
    await message.answer(
        profile_text,
        reply_markup=get_profile_keyboard()
    )


@router.callback_query(F.data == "order_history")
async def show_order_history(callback: CallbackQuery, db: Database):
    """Показать историю заказов"""
    user_id = callback.from_user.id
    orders = await db.get_user_orders(user_id, limit=10)
    
    if not orders:
        await callback.message.edit_text(
            "📦 История заказов пуста\n\n"
            "У вас пока нет покупок",
            reply_markup=get_back_keyboard()
        )
    else:
        history_text = "📦 История заказов:\n\n"
        
        for order in orders:
            created_at = datetime.fromisoformat(order['created_at']).strftime("%d.%m.%Y %H:%M")
            status_emoji = "✅" if order['status'] == "completed" else "⏳"
            
            history_text += (
                f"{status_emoji} Заказ #{order['order_id']}\n"
                f"📦 Товар: {order['product_name']}\n"
                f"💰 Сумма: {order['amount']:.2f} ₽\n"
                f"📅 Дата: {created_at}\n\n"
            )
        
        await callback.message.edit_text(
            history_text,
            reply_markup=get_back_keyboard()
        )
    
    await callback.answer()


@router.callback_query(F.data == "payment_history")
async def show_payment_history(callback: CallbackQuery, db: Database):
    """Показать историю пополнений"""
    user_id = callback.from_user.id
    payments = await db.get_user_payments(user_id, limit=10)
    
    if not payments:
        await callback.message.edit_text(
            "💳 История пополнений пуста\n\n"
            "У вас пока нет пополнений баланса",
            reply_markup=get_back_keyboard()
        )
    else:
        history_text = "💳 История пополнений:\n\n"
        
        for payment in payments:
            created_at = datetime.fromisoformat(payment['created_at']).strftime("%d.%m.%Y %H:%M")
            
            status_emoji = {
                "completed": "✅",
                "pending": "⏳",
                "cancelled": "❌"
            }.get(payment['status'], "❓")
            
            history_text += (
                f"{status_emoji} Пополнение #{payment['payment_id']}\n"
                f"💰 Сумма: {payment['amount']:.2f} ₽\n"
                f"💳 Способ: {payment['payment_method']}\n"
                f"📅 Дата: {created_at}\n\n"
            )
        
        await callback.message.edit_text(
            history_text,
            reply_markup=get_back_keyboard()
        )
    
    await callback.answer()


@router.callback_query(F.data == "add_balance")
async def add_balance(callback: CallbackQuery):
    """Пополнить баланс"""
    await callback.message.edit_text(
        "💰 Пополнение баланса\n\n"
        "🚧 Эта функция находится в разработке.\n"
        "Пожалуйста, свяжитесь с администратором для пополнения баланса.",
        reply_markup=get_back_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_profile")
async def back_to_profile(callback: CallbackQuery, db: Database):
    """Вернуться к профилю"""
    user_id = callback.from_user.id
    user_data = await db.get_user(user_id)
    
    if not user_data:
        await callback.answer("❌ Ошибка")
        return
    
    username = f"@{callback.from_user.username}" if callback.from_user.username else "Не указан"
    
    profile_text = (
        f"❤️ Пользователь: {username}\n"
        f"💸 Количество покупок: {user_data['purchases_count']}\n"
        f"💰 Ваш баланс: {user_data['balance']:.2f} ₽\n"
        f"🔑 ID: {user_id}"
    )
    
    await callback.message.edit_text(
        profile_text,
        reply_markup=get_profile_keyboard()
    )
    await callback.answer()


@router.message(F.text == "💰 Пополнить баланс")
async def add_balance_button(message: Message):
    """Обработчик кнопки пополнения баланса"""
    # Удаляем сообщение пользователя
    try:
        await message.delete()
    except Exception:
        pass
    
    await message.answer(
        "💰 Пополнение баланса\n\n"
        "🚧 Эта функция находится в разработке.\n"
        "Пожалуйста, свяжитесь с администратором для пополнения баланса."
    )

