"""
Обработчики для работы с магазином
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from ..database import Database
from ..keyboards import (
    get_categories_keyboard,
    get_products_keyboard,
    get_product_detail_keyboard
)


router = Router()


@router.message(F.text == "🛒 Купить товар")
async def show_categories(message: Message, db: Database):
    """Показать категории товаров"""
    # Удаляем сообщение пользователя
    try:
        await message.delete()
    except Exception:
        pass
    
    # Проверяем, не заблокирован ли пользователь
    user = await db.get_user(message.from_user.id)
    if user and user.get('is_blocked'):
        await message.answer(
            "🚫 Ваш аккаунт заблокирован.\n"
            "Для получения дополнительной информации обратитесь к администратору."
        )
        return
    
    categories = await db.get_active_categories()
    
    if not categories:
        await message.answer(
            "❌ В данный момент категории отсутствуют.\n"
            "Пожалуйста, попробуйте позже."
        )
        return
    
    await message.answer(
        "🛍 Активные категории в магазине:",
        reply_markup=get_categories_keyboard(categories)
    )


@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery, db: Database):
    """Вернуться к списку категорий"""
    categories = await db.get_active_categories()
    
    if not categories:
        await callback.message.edit_text(
            "❌ В данный момент категории отсутствуют.\n"
            "Пожалуйста, попробуйте позже."
        )
        await callback.answer()
        return
    
    await callback.message.edit_text(
        "🛍 Активные категории в магазине:",
        reply_markup=get_categories_keyboard(categories)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("category_"))
async def show_category_products(callback: CallbackQuery, db: Database):
    """Показать товары категории"""
    category_id = int(callback.data.split("_")[1])
    
    # Получаем информацию о категории
    category = await db.get_category(category_id)
    if not category:
        await callback.answer("❌ Категория не найдена", show_alert=True)
        return
    
    # Получаем товары категории
    products = await db.get_products_by_category(category_id, active_only=True)
    
    if not products:
        await callback.message.edit_text(
            f"📂 Категория: {category['name']}\n\n"
            f"❌ В данной категории пока нет товаров.",
            reply_markup=get_products_keyboard([], category_id)
        )
        await callback.answer()
        return
    
    # Формируем текст с описанием категории (если есть)
    text = f"📂 Категория: {category['name']}\n"
    if category.get('description'):
        text += f"\n{category['description']}\n"
    text += f"\nВыберите товар:"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_products_keyboard(products, category_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("product_"))
async def show_product_detail(callback: CallbackQuery, db: Database):
    """Показать детали товара"""
    product_id = int(callback.data.split("_")[1])
    
    # Получаем информацию о товаре
    product = await db.get_product(product_id)
    if not product:
        await callback.answer("❌ Товар не найден", show_alert=True)
        return
    
    # Формируем текст с информацией о товаре
    text = f"🎯 {product['name']}\n\n"
    
    if product.get('description'):
        text += f"📝 Описание:\n{product['description']}\n\n"
    
    text += f"💰 Цена: {product['price']} руб.\n"
    text += f"📦 В наличии: {product['stock_count']} шт.\n"
    
    if product['stock_count'] == 0:
        text += "\n❌ Товар временно отсутствует"
    
    in_stock = product['stock_count'] > 0
    
    await callback.message.edit_text(
        text,
        reply_markup=get_product_detail_keyboard(
            product_id,
            product['category_id'],
            in_stock
        )
    )
    await callback.answer()


@router.callback_query(F.data.startswith("buy_"))
async def buy_product(callback: CallbackQuery, db: Database):
    """Купить товар"""
    product_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    
    # Получаем информацию о товаре
    product = await db.get_product(product_id)
    if not product:
        await callback.answer("❌ Товар не найден", show_alert=True)
        return
    
    # Проверяем наличие товара
    if product['stock_count'] == 0:
        await callback.answer("❌ Товар закончился", show_alert=True)
        return
    
    # Получаем информацию о пользователе
    user = await db.get_user(user_id)
    if not user:
        await callback.answer("❌ Ошибка получения данных пользователя", show_alert=True)
        return
    
    # Проверяем баланс
    if user['balance'] < product['price']:
        await callback.answer(
            f"❌ Недостаточно средств!\n\n"
            f"Нужно: {product['price']} руб.\n"
            f"У вас: {user['balance']} руб.\n"
            f"Не хватает: {product['price'] - user['balance']} руб.",
            show_alert=True
        )
        return
    
    # Получаем доступный товар
    item = await db.get_available_product_item(product_id)
    if not item:
        await callback.answer("❌ Товар закончился", show_alert=True)
        # Обновляем количество товара
        await db.update_product_stock(product_id)
        return
    
    # Списываем средства
    await db.update_user_balance(user_id, -product['price'])
    
    # Отмечаем товар как проданный
    await db.mark_item_as_sold(item['item_id'], user_id)
    
    # Обновляем количество товара
    await db.update_product_stock(product_id)
    
    # Добавляем запись о покупке
    await db.add_order(user_id, product['name'], product['price'])
    
    # Увеличиваем счетчик покупок
    await db.increment_purchases(user_id)
    
    # Отправляем товар пользователю
    await callback.message.answer(
        f"✅ Покупка успешно совершена!\n\n"
        f"🎯 Товар: {product['name']}\n"
        f"💰 Цена: {product['price']} руб.\n\n"
        f"📦 Ваш товар:\n\n"
        f"<code>{item['data']}</code>\n\n"
        f"💰 Ваш новый баланс: {user['balance'] - product['price']} руб.",
        parse_mode="HTML"
    )
    
    # Обновляем сообщение с товаром
    new_balance = user['balance'] - product['price']
    await callback.message.edit_text(
        f"✅ Покупка успешно завершена!\n\n"
        f"🎯 Товар: {product['name']}\n"
        f"💰 Списано: {product['price']} руб.\n"
        f"💰 Новый баланс: {new_balance} руб.\n\n"
        f"Товар отправлен вам в личные сообщения ⬆️"
    )
    
    await callback.answer("✅ Покупка успешна!")

