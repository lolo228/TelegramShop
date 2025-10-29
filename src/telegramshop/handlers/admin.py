"""
Обработчики админ-панели
"""
import asyncio
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from ..config import BotConfig
from ..database import Database
from ..states import (
    AddCategoryStates,
    AddProductStates,
    LoadProductItemsStates,
    UserBalanceStates,
    SearchUserStates,
    BroadcastStates,
    EditInfoTextStates,
    EditCategoryStates,
    EditProductStates
)
from ..keyboards import (
    get_admin_main_keyboard,
    get_admin_products_keyboard,
    get_admin_categories_list_keyboard,
    get_admin_category_actions_keyboard,
    get_admin_products_list_keyboard,
    get_admin_product_actions_keyboard,
    get_admin_users_keyboard,
    get_admin_users_list_keyboard,
    get_admin_user_actions_keyboard,
    get_broadcast_confirm_keyboard,
    get_admin_select_category_keyboard,
    get_admin_info_texts_keyboard,
    get_admin_info_text_actions_keyboard,
    get_edit_category_fields_keyboard,
    get_edit_product_fields_keyboard
)


router = Router()


def is_admin(user_id: int, config: BotConfig) -> bool:
    """Проверка, является ли пользователь администратором"""
    return user_id in config.admin_ids


@router.callback_query(F.data == "cancel")
async def cancel_operation(callback: CallbackQuery, state: FSMContext, bot):
    """Универсальная отмена операции"""
    data = await state.get_data()
    
    # Удаляем промежуточные сообщения
    messages_to_delete = data.get('messages_to_delete', [])
    for msg_id in messages_to_delete:
        try:
            await bot.delete_message(callback.message.chat.id, msg_id)
        except Exception:
            pass
    
    # Редактируем первое сообщение
    first_bot_msg = data.get('first_bot_message_id')
    if first_bot_msg:
        try:
            await bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=first_bot_msg,
                text="❌ Операция отменена",
                reply_markup=get_admin_main_keyboard()
            )
        except Exception:
            await callback.message.edit_text(
                "❌ Операция отменена",
                reply_markup=get_admin_main_keyboard()
            )
    else:
        await callback.message.edit_text(
            "❌ Операция отменена",
            reply_markup=get_admin_main_keyboard()
        )
    
    await state.clear()
    await callback.answer()


# Главное меню админки

@router.message(Command("admin"))
async def admin_menu(message: Message, config: BotConfig):
    """Главное меню админки"""
    if not is_admin(message.from_user.id, config):
        await message.answer("❌ У вас нет доступа к админ-панели")
        return
    
    await message.answer(
        "🔧 <b>Админ-панель</b>\n\n"
        "Выберите раздел для управления:",
        reply_markup=get_admin_main_keyboard()
    )


@router.callback_query(F.data == "admin_menu")
async def admin_menu_callback(callback: CallbackQuery, config: BotConfig, state: FSMContext):
    """Возврат в главное меню админки"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    await state.clear()
    
    await callback.message.edit_text(
        "🔧 <b>Админ-панель</b>\n\n"
        "Выберите раздел для управления:",
        reply_markup=get_admin_main_keyboard()
    )
    await callback.answer()


# Управление товарами

@router.callback_query(F.data == "admin_products")
async def admin_products_menu(callback: CallbackQuery, config: BotConfig):
    """Меню управления товарами"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📦 <b>Управление товарами</b>\n\n"
        "Выберите действие:",
        reply_markup=get_admin_products_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "admin_categories_list")
async def admin_categories_list(callback: CallbackQuery, config: BotConfig, db: Database):
    """Список категорий"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    categories = await db.get_all_categories()
    
    if not categories:
        await callback.message.edit_text(
            "📂 <b>Список категорий</b>\n\n"
            "Категории отсутствуют. Создайте первую категорию!",
            reply_markup=get_admin_categories_list_keyboard([])
        )
    else:
        await callback.message.edit_text(
            f"📂 <b>Список категорий</b> (всего: {len(categories)})\n\n"
            "Выберите категорию для управления:",
            reply_markup=get_admin_categories_list_keyboard(categories)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_category_"))
async def admin_category_detail(callback: CallbackQuery, config: BotConfig, db: Database):
    """Детали категории"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    category_id = int(callback.data.split("_")[2])
    category = await db.get_category(category_id)
    
    if not category:
        await callback.answer("❌ Категория не найдена", show_alert=True)
        return
    
    status = "✅ Активна" if category['is_active'] else "❌ Неактивна"
    
    text = (
        f"📂 <b>{category['name']}</b>\n\n"
        f"Статус: {status}\n"
    )
    
    if category.get('description'):
        text += f"Описание: {category['description']}\n"
    
    text += f"Позиция: {category['position']}\n"
    
    # Получаем количество товаров в категории
    products = await db.get_products_by_category(category_id, active_only=False)
    text += f"Товаров: {len(products)}"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_admin_category_actions_keyboard(
            category_id,
            category['is_active']
        )
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_toggle_category_"))
async def admin_toggle_category(callback: CallbackQuery, config: BotConfig, db: Database):
    """Активация/деактивация категории"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    category_id = int(callback.data.split("_")[3])
    category = await db.get_category(category_id)
    
    if not category:
        await callback.answer("❌ Категория не найдена", show_alert=True)
        return
    
    new_status = not category['is_active']
    await db.update_category(category_id, is_active=new_status)
    
    status_text = "активирована" if new_status else "деактивирована"
    await callback.answer(f"✅ Категория {status_text}")
    
    # Обновляем сообщение
    await admin_category_detail(callback, config, db)


@router.callback_query(F.data.startswith("admin_delete_category_"))
async def admin_delete_category(callback: CallbackQuery, config: BotConfig, db: Database):
    """Удаление категории"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    category_id = int(callback.data.split("_")[3])
    
    # Проверяем, есть ли товары в категории
    products = await db.get_products_by_category(category_id, active_only=False)
    
    if products:
        await callback.answer(
            "❌ Невозможно удалить категорию с товарами. Сначала удалите все товары.",
            show_alert=True
        )
        return
    
    await db.delete_category(category_id)
    await callback.answer("✅ Категория удалена")
    
    # Возвращаемся к списку категорий
    await admin_categories_list(callback, config, db)


@router.callback_query(F.data.startswith("admin_edit_category_"))
async def admin_edit_category_start(callback: CallbackQuery, config: BotConfig, db: Database):
    """Начало редактирования категории"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    category_id = int(callback.data.split("_")[3])
    category = await db.get_category(category_id)
    
    if not category:
        await callback.answer("❌ Категория не найдена", show_alert=True)
        return
    
    await callback.message.edit_text(
        f"✏️ <b>Редактирование категории</b>\n\n"
        f"Категория: {category['name']}\n\n"
        f"Выберите поле для редактирования:",
        reply_markup=get_edit_category_fields_keyboard(category_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_edit_cat_name_"))
async def admin_edit_category_name_start(callback: CallbackQuery, config: BotConfig, db: Database, state: FSMContext):
    """Начало редактирования названия категории"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    category_id = int(callback.data.split("_")[4])
    category = await db.get_category(category_id)
    
    if not category:
        await callback.answer("❌ Категория не найдена", show_alert=True)
        return
    
    msg = await callback.message.edit_text(
        f"✏️ <b>Редактирование названия категории</b>\n\n"
        f"Текущее название: {category['name']}\n\n"
        f"Введите новое название категории:"
    )
    
    await state.update_data(
        category_id=category_id,
        first_bot_message_id=msg.message_id,
        messages_to_delete=[]
    )
    await state.set_state(EditCategoryStates.entering_name)
    await callback.answer()


@router.message(EditCategoryStates.entering_name)
async def admin_edit_category_name_save(message: Message, state: FSMContext, db: Database):
    """Сохранение нового названия категории"""
    data = await state.get_data()
    category_id = data['category_id']
    new_name = message.text
    
    # Обновляем название
    await db.update_category(category_id, name=new_name)
    
    # Удаляем промежуточные сообщения
    messages_to_delete = data.get('messages_to_delete', [])
    messages_to_delete.append(message.message_id)
    
    for msg_id in messages_to_delete:
        try:
            await message.bot.delete_message(message.chat.id, msg_id)
        except Exception:
            pass
    
    # Редактируем первое сообщение бота
    first_bot_msg = data.get('first_bot_message_id')
    if first_bot_msg:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=first_bot_msg,
                text=f"✅ Название категории успешно изменено на '<b>{new_name}</b>'!",
                reply_markup=get_admin_categories_list_keyboard([])
            )
        except Exception:
            await message.answer(
                f"✅ Название категории успешно изменено на '<b>{new_name}</b>'!"
            )
    else:
        await message.answer(
            f"✅ Название категории успешно изменено на '<b>{new_name}</b>'!"
        )
    
    await state.clear()


@router.callback_query(F.data.startswith("admin_edit_cat_desc_"))
async def admin_edit_category_desc_start(callback: CallbackQuery, config: BotConfig, db: Database, state: FSMContext):
    """Начало редактирования описания категории"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    category_id = int(callback.data.split("_")[4])
    category = await db.get_category(category_id)
    
    if not category:
        await callback.answer("❌ Категория не найдена", show_alert=True)
        return
    
    current_desc = category.get('description', 'Не установлено')
    
    msg = await callback.message.edit_text(
        f"✏️ <b>Редактирование описания категории</b>\n\n"
        f"Текущее описание: {current_desc}\n\n"
        f"Введите новое описание категории (или '-' для удаления):"
    )
    
    await state.update_data(
        category_id=category_id,
        first_bot_message_id=msg.message_id,
        messages_to_delete=[]
    )
    await state.set_state(EditCategoryStates.entering_description)
    await callback.answer()


@router.message(EditCategoryStates.entering_description)
async def admin_edit_category_desc_save(message: Message, state: FSMContext, db: Database):
    """Сохранение нового описания категории"""
    data = await state.get_data()
    category_id = data['category_id']
    new_desc = "" if message.text == "-" else message.text
    
    # Обновляем описание
    await db.update_category(category_id, description=new_desc)
    
    # Удаляем промежуточные сообщения
    messages_to_delete = data.get('messages_to_delete', [])
    messages_to_delete.append(message.message_id)
    
    for msg_id in messages_to_delete:
        try:
            await message.bot.delete_message(message.chat.id, msg_id)
        except Exception:
            pass
    
    # Редактируем первое сообщение бота
    first_bot_msg = data.get('first_bot_message_id')
    result_text = "✅ Описание категории успешно изменено!" if new_desc else "✅ Описание категории успешно удалено!"
    
    if first_bot_msg:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=first_bot_msg,
                text=result_text,
                reply_markup=get_admin_categories_list_keyboard([])
            )
        except Exception:
            await message.answer(result_text)
    else:
        await message.answer(result_text)
    
    await state.clear()


@router.callback_query(F.data == "admin_add_category")
async def admin_add_category_start(callback: CallbackQuery, config: BotConfig, state: FSMContext):
    """Начало добавления категории"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    msg = await callback.message.edit_text(
        "➕ <b>Добавление категории</b>\n\n"
        "Введите название категории:"
    )
    # Сохраняем ID первого сообщения бота для последующего редактирования
    await state.update_data(
        first_bot_message_id=msg.message_id,
        messages_to_delete=[]
    )
    await state.set_state(AddCategoryStates.name)
    await callback.answer()


@router.message(AddCategoryStates.name)
async def admin_add_category_name(message: Message, state: FSMContext):
    """Получение названия категории"""
    data = await state.get_data()
    messages_to_delete = data.get('messages_to_delete', [])
    messages_to_delete.append(message.message_id)  # Добавляем сообщение пользователя
    
    await state.update_data(
        name=message.text,
        messages_to_delete=messages_to_delete
    )
    
    msg = await message.answer(
        "➕ <b>Добавление категории</b>\n\n"
        "Введите описание категории (или отправьте '-' для пропуска):"
    )
    messages_to_delete.append(msg.message_id)  # Добавляем промежуточное сообщение бота
    await state.update_data(messages_to_delete=messages_to_delete)
    await state.set_state(AddCategoryStates.description)


@router.message(AddCategoryStates.description)
async def admin_add_category_description(message: Message, state: FSMContext, db: Database):
    """Получение описания и создание категории"""
    data = await state.get_data()
    description = "" if message.text == "-" else message.text
    
    category_id = await db.add_category(
        name=data['name'],
        description=description
    )
    
    # Удаляем все промежуточные сообщения
    messages_to_delete = data.get('messages_to_delete', [])
    messages_to_delete.append(message.message_id)  # Последнее сообщение пользователя
    
    for msg_id in messages_to_delete:
        try:
            await message.bot.delete_message(message.chat.id, msg_id)
        except Exception:
            pass
    
    # Редактируем первое сообщение бота
    first_bot_msg = data.get('first_bot_message_id')
    if first_bot_msg:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=first_bot_msg,
                text=f"✅ Категория '<b>{data['name']}</b>' успешно создана!\n\n"
                     f"ID категории: {category_id}",
                reply_markup=get_admin_products_keyboard()
            )
        except Exception:
            await message.answer(
                f"✅ Категория '<b>{data['name']}</b>' успешно создана!\n\n"
                f"ID категории: {category_id}"
            )
    else:
        await message.answer(
            f"✅ Категория '<b>{data['name']}</b>' успешно создана!\n\n"
            f"ID категории: {category_id}"
        )
    
    await state.clear()


@router.callback_query(F.data == "admin_products_list")
async def admin_products_list(callback: CallbackQuery, config: BotConfig, db: Database):
    """Список товаров"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    products = await db.get_all_products()
    
    if not products:
        await callback.message.edit_text(
            "📦 <b>Список товаров</b>\n\n"
            "Товары отсутствуют. Создайте первый товар!",
            reply_markup=get_admin_products_list_keyboard([])
        )
    else:
        await callback.message.edit_text(
            f"📦 <b>Список товаров</b> (всего: {len(products)})\n\n"
            "Выберите товар для управления:",
            reply_markup=get_admin_products_list_keyboard(products)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_product_"))
async def admin_product_detail(callback: CallbackQuery, config: BotConfig, db: Database):
    """Детали товара"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    # Извлекаем ID товара из callback_data
    parts = callback.data.split("_")
    if len(parts) < 3:
        await callback.answer("❌ Неверный формат данных", show_alert=True)
        return
    
    try:
        product_id = int(parts[2])
    except (ValueError, IndexError):
        await callback.answer("❌ Неверный ID товара", show_alert=True)
        return
    
    product = await db.get_product(product_id)
    
    if not product:
        await callback.answer("❌ Товар не найден", show_alert=True)
        return
    
    category = await db.get_category(product['category_id'])
    category_name = category['name'] if category else "Без категории"
    
    status = "✅ Активен" if product['is_active'] else "❌ Неактивен"
    
    text = (
        f"📦 <b>{product['name']}</b>\n\n"
        f"Категория: {category_name}\n"
        f"Цена: {product['price']} руб.\n"
        f"В наличии: {product['stock_count']} шт.\n"
        f"Статус: {status}\n"
    )
    
    if product.get('description'):
        text += f"\nОписание: {product['description']}"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_admin_product_actions_keyboard(
            product_id,
            product['is_active']
        )
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_toggle_product_"))
async def admin_toggle_product(callback: CallbackQuery, config: BotConfig, db: Database):
    """Активация/деактивация товара"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    product_id = int(callback.data.split("_")[3])
    product = await db.get_product(product_id)
    
    if not product:
        await callback.answer("❌ Товар не найден", show_alert=True)
        return
    
    new_status = not product['is_active']
    await db.update_product(product_id, is_active=new_status)
    
    status_text = "активирован" if new_status else "деактивирован"
    await callback.answer(f"✅ Товар {status_text}")
    
    # Обновляем сообщение
    await admin_product_detail(callback, config, db)


@router.callback_query(F.data.startswith("admin_delete_product_"))
async def admin_delete_product(callback: CallbackQuery, config: BotConfig, db: Database):
    """Удаление товара"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    product_id = int(callback.data.split("_")[3])
    
    await db.delete_product(product_id)
    await callback.answer("✅ Товар удален")
    
    # Возвращаемся к списку товаров
    await admin_products_list(callback, config, db)


@router.callback_query(F.data.startswith("admin_edit_product_"))
async def admin_edit_product_start(callback: CallbackQuery, config: BotConfig, db: Database):
    """Начало редактирования товара"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    # Извлекаем ID товара из callback_data
    parts = callback.data.split("_")
    if len(parts) < 4:
        await callback.answer("❌ Неверный формат данных", show_alert=True)
        return
    
    try:
        product_id = int(parts[3])
    except (ValueError, IndexError):
        await callback.answer("❌ Неверный ID товара", show_alert=True)
        return
    
    product = await db.get_product(product_id)
    
    if not product:
        await callback.answer("❌ Товар не найден", show_alert=True)
        return
    
    await callback.message.edit_text(
        f"✏️ <b>Редактирование товара</b>\n\n"
        f"Товар: {product['name']}\n\n"
        f"Выберите поле для редактирования:",
        reply_markup=get_edit_product_fields_keyboard(product_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_edit_prod_name_"))
async def admin_edit_product_name_start(callback: CallbackQuery, config: BotConfig, db: Database, state: FSMContext):
    """Начало редактирования названия товара"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    product_id = int(callback.data.split("_")[4])
    product = await db.get_product(product_id)
    
    if not product:
        await callback.answer("❌ Товар не найден", show_alert=True)
        return
    
    msg = await callback.message.edit_text(
        f"✏️ <b>Редактирование названия товара</b>\n\n"
        f"Текущее название: {product['name']}\n\n"
        f"Введите новое название товара:"
    )
    
    await state.update_data(
        product_id=product_id,
        first_bot_message_id=msg.message_id,
        messages_to_delete=[]
    )
    await state.set_state(EditProductStates.entering_name)
    await callback.answer()


@router.message(EditProductStates.entering_name)
async def admin_edit_product_name_save(message: Message, state: FSMContext, db: Database):
    """Сохранение нового названия товара"""
    data = await state.get_data()
    product_id = data['product_id']
    new_name = message.text
    
    # Обновляем название
    await db.update_product(product_id, name=new_name)
    
    # Удаляем промежуточные сообщения
    messages_to_delete = data.get('messages_to_delete', [])
    messages_to_delete.append(message.message_id)
    
    for msg_id in messages_to_delete:
        try:
            await message.bot.delete_message(message.chat.id, msg_id)
        except Exception:
            pass
    
    # Редактируем первое сообщение бота
    first_bot_msg = data.get('first_bot_message_id')
    if first_bot_msg:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=first_bot_msg,
                text=f"✅ Название товара успешно изменено на '<b>{new_name}</b>'!",
                reply_markup=get_admin_products_list_keyboard([])
            )
        except Exception:
            await message.answer(
                f"✅ Название товара успешно изменено на '<b>{new_name}</b>'!"
            )
    else:
        await message.answer(
            f"✅ Название товара успешно изменено на '<b>{new_name}</b>'!"
        )
    
    await state.clear()


@router.callback_query(F.data.startswith("admin_edit_prod_desc_"))
async def admin_edit_product_desc_start(callback: CallbackQuery, config: BotConfig, db: Database, state: FSMContext):
    """Начало редактирования описания товара"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    product_id = int(callback.data.split("_")[4])
    product = await db.get_product(product_id)
    
    if not product:
        await callback.answer("❌ Товар не найден", show_alert=True)
        return
    
    current_desc = product.get('description', 'Не установлено')
    
    msg = await callback.message.edit_text(
        f"✏️ <b>Редактирование описания товара</b>\n\n"
        f"Текущее описание: {current_desc}\n\n"
        f"Введите новое описание товара (или '-' для удаления):"
    )
    
    await state.update_data(
        product_id=product_id,
        first_bot_message_id=msg.message_id,
        messages_to_delete=[]
    )
    await state.set_state(EditProductStates.entering_description)
    await callback.answer()


@router.message(EditProductStates.entering_description)
async def admin_edit_product_desc_save(message: Message, state: FSMContext, db: Database):
    """Сохранение нового описания товара"""
    data = await state.get_data()
    product_id = data['product_id']
    new_desc = "" if message.text == "-" else message.text
    
    # Обновляем описание
    await db.update_product(product_id, description=new_desc)
    
    # Удаляем промежуточные сообщения
    messages_to_delete = data.get('messages_to_delete', [])
    messages_to_delete.append(message.message_id)
    
    for msg_id in messages_to_delete:
        try:
            await message.bot.delete_message(message.chat.id, msg_id)
        except Exception:
            pass
    
    # Редактируем первое сообщение бота
    first_bot_msg = data.get('first_bot_message_id')
    result_text = "✅ Описание товара успешно изменено!" if new_desc else "✅ Описание товара успешно удалено!"
    
    if first_bot_msg:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=first_bot_msg,
                text=result_text,
                reply_markup=get_admin_products_list_keyboard([])
            )
        except Exception:
            await message.answer(result_text)
    else:
        await message.answer(result_text)
    
    await state.clear()


@router.callback_query(F.data.startswith("admin_edit_prod_price_"))
async def admin_edit_product_price_start(callback: CallbackQuery, config: BotConfig, db: Database, state: FSMContext):
    """Начало редактирования цены товара"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    product_id = int(callback.data.split("_")[4])
    product = await db.get_product(product_id)
    
    if not product:
        await callback.answer("❌ Товар не найден", show_alert=True)
        return
    
    msg = await callback.message.edit_text(
        f"✏️ <b>Редактирование цены товара</b>\n\n"
        f"Текущая цена: {product['price']} руб.\n\n"
        f"Введите новую цену товара (только число):"
    )
    
    await state.update_data(
        product_id=product_id,
        first_bot_message_id=msg.message_id,
        messages_to_delete=[]
    )
    await state.set_state(EditProductStates.entering_price)
    await callback.answer()


@router.message(EditProductStates.entering_price)
async def admin_edit_product_price_save(message: Message, state: FSMContext, db: Database):
    """Сохранение новой цены товара"""
    data = await state.get_data()
    product_id = data['product_id']
    messages_to_delete = data.get('messages_to_delete', [])
    
    try:
        new_price = float(message.text)
        if new_price <= 0:
            raise ValueError
    except ValueError:
        msg = await message.answer("❌ Неверная цена. Введите положительное число:")
        messages_to_delete.append(message.message_id)
        messages_to_delete.append(msg.message_id)
        await state.update_data(messages_to_delete=messages_to_delete)
        return
    
    # Обновляем цену
    await db.update_product(product_id, price=new_price)
    
    # Удаляем промежуточные сообщения
    messages_to_delete.append(message.message_id)
    
    for msg_id in messages_to_delete:
        try:
            await message.bot.delete_message(message.chat.id, msg_id)
        except Exception:
            pass
    
    # Редактируем первое сообщение бота
    first_bot_msg = data.get('first_bot_message_id')
    if first_bot_msg:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=first_bot_msg,
                text=f"✅ Цена товара успешно изменена на <b>{new_price} руб.</b>!",
                reply_markup=get_admin_products_list_keyboard([])
            )
        except Exception:
            await message.answer(
                f"✅ Цена товара успешно изменена на <b>{new_price} руб.</b>!"
            )
    else:
        await message.answer(
            f"✅ Цена товара успешно изменена на <b>{new_price} руб.</b>!"
        )
    
    await state.clear()


@router.callback_query(F.data == "admin_add_product")
async def admin_add_product_start(callback: CallbackQuery, config: BotConfig, db: Database, state: FSMContext):
    """Начало добавления товара"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    categories = await db.get_all_categories()
    
    if not categories:
        await callback.answer(
            "❌ Сначала создайте хотя бы одну категорию!",
            show_alert=True
        )
        return
    
    msg = await callback.message.edit_text(
        "➕ <b>Добавление товара</b>\n\n"
        "Выберите категорию для товара:",
        reply_markup=get_admin_select_category_keyboard(categories)
    )
    # Сохраняем ID первого сообщения бота
    await state.update_data(
        first_bot_message_id=msg.message_id,
        messages_to_delete=[]
    )
    await state.set_state(AddProductStates.category)
    await callback.answer()


@router.callback_query(AddProductStates.category, F.data.startswith("admin_select_cat_"))
async def admin_add_product_category(callback: CallbackQuery, state: FSMContext):
    """Выбор категории для товара"""
    category_id = int(callback.data.split("_")[3])
    data = await state.get_data()
    
    await state.update_data(
        category_id=category_id,
        first_bot_message_id=data.get('first_bot_message_id'),
        messages_to_delete=data.get('messages_to_delete', [])
    )
    
    await callback.message.edit_text(
        "➕ <b>Добавление товара</b>\n\n"
        "Введите название товара:"
    )
    await state.set_state(AddProductStates.name)
    await callback.answer()


@router.message(AddProductStates.name)
async def admin_add_product_name(message: Message, state: FSMContext):
    """Получение названия товара"""
    data = await state.get_data()
    messages_to_delete = data.get('messages_to_delete', [])
    messages_to_delete.append(message.message_id)
    
    await state.update_data(
        name=message.text,
        messages_to_delete=messages_to_delete
    )
    
    msg = await message.answer(
        "➕ <b>Добавление товара</b>\n\n"
        "Введите описание товара (или отправьте '-' для пропуска):"
    )
    messages_to_delete.append(msg.message_id)
    await state.update_data(messages_to_delete=messages_to_delete)
    await state.set_state(AddProductStates.description)


@router.message(AddProductStates.description)
async def admin_add_product_description(message: Message, state: FSMContext):
    """Получение описания товара"""
    description = "" if message.text == "-" else message.text
    data = await state.get_data()
    messages_to_delete = data.get('messages_to_delete', [])
    messages_to_delete.append(message.message_id)
    
    await state.update_data(
        description=description,
        messages_to_delete=messages_to_delete
    )
    
    msg = await message.answer(
        "➕ <b>Добавление товара</b>\n\n"
        "Введите цену товара (только число):"
    )
    messages_to_delete.append(msg.message_id)
    await state.update_data(messages_to_delete=messages_to_delete)
    await state.set_state(AddProductStates.price)


@router.message(AddProductStates.price)
async def admin_add_product_price(message: Message, state: FSMContext, db: Database):
    """Получение цены и создание товара"""
    data = await state.get_data()
    messages_to_delete = data.get('messages_to_delete', [])
    
    try:
        price = float(message.text)
        if price <= 0:
            raise ValueError
    except ValueError:
        msg = await message.answer("❌ Неверная цена. Введите положительное число:")
        messages_to_delete.append(message.message_id)
        messages_to_delete.append(msg.message_id)
        await state.update_data(messages_to_delete=messages_to_delete)
        return
    
    product_id = await db.add_product(
        category_id=data['category_id'],
        name=data['name'],
        description=data['description'],
        price=price
    )
    
    # Удаляем промежуточные сообщения
    messages_to_delete.append(message.message_id)
    for msg_id in messages_to_delete:
        try:
            await message.bot.delete_message(message.chat.id, msg_id)
        except Exception:
            pass
    
    # Редактируем первое сообщение бота
    first_bot_msg = data.get('first_bot_message_id')
    if first_bot_msg:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=first_bot_msg,
                text=f"✅ Товар '<b>{data['name']}</b>' успешно создан!\n\n"
                     f"ID товара: {product_id}\n"
                     f"Цена: {price} руб.\n\n"
                     f"Теперь вы можете загрузить товарные позиции для этого товара.",
                reply_markup=get_admin_products_keyboard()
            )
        except Exception:
            await message.answer(
                f"✅ Товар '<b>{data['name']}</b>' успешно создан!\n\n"
                f"ID товара: {product_id}\n"
                f"Цена: {price} руб."
            )
    else:
        await message.answer(
            f"✅ Товар '<b>{data['name']}</b>' успешно создан!\n\n"
            f"ID товара: {product_id}\n"
            f"Цена: {price} руб."
        )
    
    await state.clear()


@router.callback_query(F.data.startswith("admin_load_items_"))
async def admin_load_items_start(callback: CallbackQuery, config: BotConfig, db: Database, state: FSMContext):
    """Начало загрузки товарных позиций"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    product_id = int(callback.data.split("_")[3])
    product = await db.get_product(product_id)
    
    if not product:
        await callback.answer("❌ Товар не найден", show_alert=True)
        return
    
    msg = await callback.message.edit_text(
        f"📥 <b>Загрузка товарных позиций</b>\n\n"
        f"Товар: {product['name']}\n\n"
        f"Отправьте товарные позиции (каждая с новой строки).\n"
        f"Например:\n"
        f"<code>login1:password1\n"
        f"login2:password2\n"
        f"login3:password3</code>\n\n"
        f"Или отправьте текстовый файл."
    )
    
    await state.update_data(
        product_id=product_id,
        first_bot_message_id=msg.message_id,
        messages_to_delete=[]
    )
    await state.set_state(LoadProductItemsStates.entering_items)
    await callback.answer()


@router.message(LoadProductItemsStates.entering_items, F.text)
async def admin_load_items_text(message: Message, state: FSMContext, db: Database):
    """Загрузка товарных позиций из текста"""
    data = await state.get_data()
    product_id = data['product_id']
    
    # Разбиваем текст на строки
    items = [line.strip() for line in message.text.split('\n') if line.strip()]
    
    if not items:
        await message.answer("❌ Не найдено ни одной товарной позиции")
        return
    
    count = await db.add_product_items_bulk(product_id, items)
    
    # Удаляем промежуточные сообщения
    messages_to_delete = data.get('messages_to_delete', [])
    messages_to_delete.append(message.message_id)
    
    for msg_id in messages_to_delete:
        try:
            await message.bot.delete_message(message.chat.id, msg_id)
        except Exception:
            pass
    
    # Редактируем первое сообщение
    first_bot_msg = data.get('first_bot_message_id')
    if first_bot_msg:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=first_bot_msg,
                text=f"✅ Успешно загружено <b>{count}</b> товарных позиций!",
                reply_markup=get_admin_products_keyboard()
            )
        except Exception:
            await message.answer(f"✅ Успешно загружено <b>{count}</b> товарных позиций!")
    else:
        await message.answer(f"✅ Успешно загружено <b>{count}</b> товарных позиций!")
    
    await state.clear()


@router.message(LoadProductItemsStates.entering_items, F.document)
async def admin_load_items_file(message: Message, state: FSMContext, db: Database, bot):
    """Загрузка товарных позиций из файла"""
    data = await state.get_data()
    product_id = data['product_id']
    
    # Скачиваем файл
    file = await bot.get_file(message.document.file_id)
    file_content = await bot.download_file(file.file_path)
    
    # Читаем содержимое
    text = file_content.read().decode('utf-8')
    items = [line.strip() for line in text.split('\n') if line.strip()]
    
    if not items:
        await message.answer("❌ Файл пуст или не содержит данных")
        return
    
    count = await db.add_product_items_bulk(product_id, items)
    
    # Удаляем промежуточные сообщения
    messages_to_delete = data.get('messages_to_delete', [])
    messages_to_delete.append(message.message_id)
    
    for msg_id in messages_to_delete:
        try:
            await message.bot.delete_message(message.chat.id, msg_id)
        except Exception:
            pass
    
    # Редактируем первое сообщение
    first_bot_msg = data.get('first_bot_message_id')
    if first_bot_msg:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=first_bot_msg,
                text=f"✅ Успешно загружено <b>{count}</b> товарных позиций из файла!",
                reply_markup=get_admin_products_keyboard()
            )
        except Exception:
            await message.answer(f"✅ Успешно загружено <b>{count}</b> товарных позиций из файла!")
    else:
        await message.answer(f"✅ Успешно загружено <b>{count}</b> товарных позиций из файла!")
    
    await state.clear()


# Управление пользователями

@router.callback_query(F.data == "admin_users")
async def admin_users_menu(callback: CallbackQuery, config: BotConfig):
    """Меню управления пользователями"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    await callback.message.edit_text(
        "👥 <b>Управление пользователями</b>\n\n"
        "Выберите действие:",
        reply_markup=get_admin_users_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_users_list_"))
async def admin_users_list(callback: CallbackQuery, config: BotConfig, db: Database):
    """Список пользователей с пагинацией"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    page = int(callback.data.split("_")[3])
    limit = 10
    offset = page * limit
    
    users = await db.get_all_users(limit=limit, offset=offset)
    total_count = await db.get_users_count()
    total_pages = (total_count + limit - 1) // limit
    
    if not users:
        await callback.message.edit_text(
            "👥 <b>Список пользователей</b>\n\n"
            "Пользователи отсутствуют.",
            reply_markup=get_admin_users_list_keyboard([], page, total_pages)
        )
    else:
        await callback.message.edit_text(
            f"👥 <b>Список пользователей</b>\n\n"
            f"Страница {page + 1} из {total_pages}\n"
            f"Всего пользователей: {total_count}",
            reply_markup=get_admin_users_list_keyboard(users, page, total_pages)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_user_"))
async def admin_user_detail(callback: CallbackQuery, config: BotConfig, db: Database):
    """Детали пользователя"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    user_id = int(callback.data.split("_")[2])
    user = await db.get_user(user_id)
    
    if not user:
        await callback.answer("❌ Пользователь не найден", show_alert=True)
        return
    
    username = f"@{user['username']}" if user.get('username') else "Нет username"
    status = "🚫 Заблокирован" if user.get('is_blocked') else "✅ Активен"
    
    text = (
        f"👤 <b>{user['first_name']}</b>\n\n"
        f"ID: <code>{user['user_id']}</code>\n"
        f"Username: {username}\n"
        f"Баланс: {user['balance']} руб.\n"
        f"Покупок: {user['purchases_count']}\n"
        f"Статус: {status}\n"
        f"Регистрация: {user['created_at']}"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_admin_user_actions_keyboard(
            user_id,
            user.get('is_blocked', False)
        )
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_toggle_block_"))
async def admin_toggle_block_user(callback: CallbackQuery, config: BotConfig, db: Database):
    """Блокировка/разблокировка пользователя"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    user_id = int(callback.data.split("_")[3])
    user = await db.get_user(user_id)
    
    if not user:
        await callback.answer("❌ Пользователь не найден", show_alert=True)
        return
    
    new_status = not user.get('is_blocked', False)
    await db.set_user_blocked(user_id, new_status)
    
    status_text = "заблокирован" if new_status else "разблокирован"
    await callback.answer(f"✅ Пользователь {status_text}")
    
    # Обновляем сообщение
    await admin_user_detail(callback, config, db)


@router.callback_query(F.data.startswith("admin_change_balance_"))
async def admin_change_balance_start(callback: CallbackQuery, config: BotConfig, state: FSMContext):
    """Начало изменения баланса"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    user_id = int(callback.data.split("_")[3])
    
    msg = await callback.message.edit_text(
        "💰 <b>Изменение баланса</b>\n\n"
        "Введите сумму для изменения баланса:\n"
        "• Положительное число для пополнения\n"
        "• Отрицательное число для списания\n\n"
        "Например: 100 или -50"
    )
    
    await state.update_data(
        user_id=user_id,
        first_bot_message_id=msg.message_id,
        messages_to_delete=[]
    )
    await state.set_state(UserBalanceStates.entering_amount)
    await callback.answer()


@router.message(UserBalanceStates.entering_amount)
async def admin_change_balance_amount(message: Message, state: FSMContext, db: Database):
    """Изменение баланса пользователя"""
    data = await state.get_data()
    messages_to_delete = data.get('messages_to_delete', [])
    
    try:
        amount = float(message.text)
    except ValueError:
        msg = await message.answer("❌ Неверная сумма. Введите число:")
        messages_to_delete.append(message.message_id)
        messages_to_delete.append(msg.message_id)
        await state.update_data(messages_to_delete=messages_to_delete)
        return
    
    user_id = data['user_id']
    
    user = await db.get_user(user_id)
    if not user:
        await message.answer("❌ Пользователь не найден")
        await state.clear()
        return
    
    await db.update_user_balance(user_id, amount)
    
    action = "пополнен" if amount > 0 else "списан"
    new_balance = user['balance'] + amount
    
    # Удаляем промежуточные сообщения
    messages_to_delete.append(message.message_id)
    for msg_id in messages_to_delete:
        try:
            await message.bot.delete_message(message.chat.id, msg_id)
        except Exception:
            pass
    
    # Редактируем первое сообщение
    first_bot_msg = data.get('first_bot_message_id')
    if first_bot_msg:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=first_bot_msg,
                text=f"✅ Баланс пользователя {action}!\n\n"
                     f"Сумма: {abs(amount)} руб.\n"
                     f"Новый баланс: {new_balance} руб.",
                reply_markup=get_admin_users_keyboard()
            )
        except Exception:
            await message.answer(
                f"✅ Баланс пользователя {action}!\n\n"
                f"Сумма: {abs(amount)} руб.\n"
                f"Новый баланс: {new_balance} руб."
            )
    else:
        await message.answer(
            f"✅ Баланс пользователя {action}!\n\n"
            f"Сумма: {abs(amount)} руб.\n"
            f"Новый баланс: {new_balance} руб."
        )
    
    await state.clear()


@router.callback_query(F.data == "admin_search_user")
async def admin_search_user_start(callback: CallbackQuery, config: BotConfig, state: FSMContext):
    """Начало поиска пользователя"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    msg = await callback.message.edit_text(
        "🔍 <b>Поиск пользователя</b>\n\n"
        "Введите ID пользователя или username:"
    )
    
    await state.update_data(
        first_bot_message_id=msg.message_id,
        messages_to_delete=[]
    )
    await state.set_state(SearchUserStates.entering_query)
    await callback.answer()


@router.message(SearchUserStates.entering_query)
async def admin_search_user_query(message: Message, state: FSMContext, db: Database):
    """Поиск пользователя"""
    data = await state.get_data()
    query = message.text.strip().replace('@', '')
    
    users = await db.search_users(query)
    
    # Удаляем промежуточные сообщения
    messages_to_delete = data.get('messages_to_delete', [])
    messages_to_delete.append(message.message_id)
    
    for msg_id in messages_to_delete:
        try:
            await message.bot.delete_message(message.chat.id, msg_id)
        except Exception:
            pass
    
    first_bot_msg = data.get('first_bot_message_id')
    
    if not users:
        if first_bot_msg:
            try:
                await message.bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=first_bot_msg,
                    text="❌ Пользователи не найдены.\n\nПопробуйте другой запрос.",
                    reply_markup=get_admin_users_keyboard()
                )
            except Exception:
                await message.answer("❌ Пользователи не найдены.\n\nПопробуйте другой запрос.")
        else:
            await message.answer("❌ Пользователи не найдены.\n\nПопробуйте другой запрос.")
        await state.clear()
        return
    
    await state.clear()
    
    if len(users) == 1:
        # Если найден один пользователь, показываем его детали
        user = users[0]
        username = f"@{user['username']}" if user.get('username') else "Нет username"
        status = "🚫 Заблокирован" if user.get('is_blocked') else "✅ Активен"
        
        text = (
            f"👤 <b>{user['first_name']}</b>\n\n"
            f"ID: <code>{user['user_id']}</code>\n"
            f"Username: {username}\n"
            f"Баланс: {user['balance']} руб.\n"
            f"Покупок: {user['purchases_count']}\n"
            f"Статус: {status}\n"
            f"Регистрация: {user['created_at']}"
        )
        
        if first_bot_msg:
            try:
                await message.bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=first_bot_msg,
                    text=text,
                    reply_markup=get_admin_user_actions_keyboard(
                        user['user_id'],
                        user.get('is_blocked', False)
                    )
                )
            except Exception:
                await message.answer(
                    text,
                    reply_markup=get_admin_user_actions_keyboard(
                        user['user_id'],
                        user.get('is_blocked', False)
                    )
                )
        else:
            await message.answer(
                text,
                reply_markup=get_admin_user_actions_keyboard(
                    user['user_id'],
                    user.get('is_blocked', False)
                )
            )
    else:
        # Если найдено несколько, показываем список
        text = f"🔍 <b>Найдено пользователей:</b> {len(users)}\n\n"
        
        for user in users[:10]:  # Показываем первых 10
            username = f"@{user['username']}" if user.get('username') else user['first_name']
            status = "🚫" if user.get('is_blocked') else "✅"
            text += f"{status} {username} (ID: {user['user_id']}) - {user['balance']}₽\n"
        
        if first_bot_msg:
            try:
                await message.bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=first_bot_msg,
                    text=text,
                    reply_markup=get_admin_users_list_keyboard(users[:10], 0, 1)
                )
            except Exception:
                await message.answer(
                    text,
                    reply_markup=get_admin_users_list_keyboard(users[:10], 0, 1)
                )
        else:
            await message.answer(
                text,
                reply_markup=get_admin_users_list_keyboard(users[:10], 0, 1)
            )


# Статистика

@router.callback_query(F.data == "admin_stats")
async def admin_statistics(callback: CallbackQuery, config: BotConfig, db: Database):
    """Показ статистики"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    stats = await db.get_statistics()
    
    text = (
        "📊 <b>Статистика магазина</b>\n\n"
        f"👥 Пользователей: {stats['users_count']}\n"
        f"📦 Заказов: {stats['orders_count']}\n"
        f"💰 Выручка: {stats['revenue']} руб.\n\n"
        f"📂 Активных категорий: {stats['active_categories']}\n"
        f"🛍 Активных товаров: {stats['active_products']}\n"
        f"📥 Товаров в наличии: {stats['items_in_stock']}"
    )
    
    from ..keyboards import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄 Обновить",
                    callback_data="admin_stats"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ Назад в меню",
                    callback_data="admin_menu"
                )
            ]
        ]
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


# Рассылка

@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(callback: CallbackQuery, config: BotConfig, state: FSMContext):
    """Начало рассылки"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    msg = await callback.message.edit_text(
        "📢 <b>Рассылка сообщений</b>\n\n"
        "Введите текст сообщения для рассылки:\n\n"
        "Поддерживается HTML форматирование."
    )
    
    await state.update_data(
        first_bot_message_id=msg.message_id,
        messages_to_delete=[]
    )
    await state.set_state(BroadcastStates.entering_message)
    await callback.answer()


@router.message(BroadcastStates.entering_message)
async def admin_broadcast_message(message: Message, state: FSMContext, db: Database):
    """Получение текста рассылки и подтверждение"""
    data = await state.get_data()
    messages_to_delete = data.get('messages_to_delete', [])
    messages_to_delete.append(message.message_id)
    
    await state.update_data(
        message_text=message.text,
        messages_to_delete=messages_to_delete
    )
    
    # Получаем количество пользователей
    users_count = await db.get_users_count()
    
    msg = await message.answer(
        f"📢 <b>Подтверждение рассылки</b>\n\n"
        f"Текст сообщения:\n\n"
        f"{message.text}\n\n"
        f"Количество получателей: {users_count}\n\n"
        f"Подтвердите отправку:",
        reply_markup=get_broadcast_confirm_keyboard()
    )
    messages_to_delete.append(msg.message_id)
    await state.update_data(messages_to_delete=messages_to_delete)
    await state.set_state(BroadcastStates.confirming)


@router.callback_query(BroadcastStates.confirming, F.data == "admin_broadcast_confirm")
async def admin_broadcast_confirm(callback: CallbackQuery, state: FSMContext, db: Database, bot):
    """Подтверждение и отправка рассылки"""
    data = await state.get_data()
    message_text = data['message_text']
    
    # Удаляем промежуточные сообщения
    messages_to_delete = data.get('messages_to_delete', [])
    for msg_id in messages_to_delete:
        try:
            await bot.delete_message(callback.message.chat.id, msg_id)
        except Exception:
            pass
    
    # Редактируем первое сообщение на статус "Идет рассылка"
    first_bot_msg = data.get('first_bot_message_id')
    if first_bot_msg:
        try:
            await bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=first_bot_msg,
                text="📢 <b>Рассылка начата...</b>\n\nПожалуйста, подождите."
            )
        except Exception:
            pass
    else:
        await callback.message.edit_text(
            "📢 <b>Рассылка начата...</b>\n\nПожалуйста, подождите."
        )
    
    # Получаем всех пользователей
    all_users = []
    offset = 0
    limit = 100
    
    while True:
        users = await db.get_all_users(limit=limit, offset=offset)
        if not users:
            break
        all_users.extend(users)
        offset += limit
    
    # Отправляем сообщения
    success = 0
    failed = 0
    
    for user in all_users:
        try:
            await bot.send_message(user['user_id'], message_text)
            success += 1
            await asyncio.sleep(0.05)  # Небольшая задержка между сообщениями
        except Exception:
            failed += 1
    
    # Редактируем сообщение на результат
    msg_id_to_edit = first_bot_msg if first_bot_msg else callback.message.message_id
    try:
        await bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=msg_id_to_edit,
            text=f"✅ <b>Рассылка завершена!</b>\n\n"
                 f"Успешно отправлено: {success}\n"
                 f"Не удалось отправить: {failed}",
            reply_markup=get_admin_main_keyboard()
        )
    except Exception:
        await callback.message.answer(
            f"✅ <b>Рассылка завершена!</b>\n\n"
            f"Успешно отправлено: {success}\n"
            f"Не удалось отправить: {failed}"
        )
    
    await state.clear()
    await callback.answer()


@router.callback_query(BroadcastStates.confirming, F.data == "admin_broadcast_cancel")
async def admin_broadcast_cancel(callback: CallbackQuery, state: FSMContext, bot):
    """Отмена рассылки"""
    data = await state.get_data()
    
    # Удаляем промежуточные сообщения
    messages_to_delete = data.get('messages_to_delete', [])
    for msg_id in messages_to_delete:
        try:
            await bot.delete_message(callback.message.chat.id, msg_id)
        except Exception:
            pass
    
    # Редактируем первое сообщение
    first_bot_msg = data.get('first_bot_message_id')
    if first_bot_msg:
        try:
            await bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=first_bot_msg,
                text="❌ Рассылка отменена",
                reply_markup=get_admin_main_keyboard()
            )
        except Exception:
            await callback.message.edit_text(
                "❌ Рассылка отменена",
                reply_markup=get_admin_main_keyboard()
            )
    else:
        await callback.message.edit_text(
            "❌ Рассылка отменена",
            reply_markup=get_admin_main_keyboard()
        )
    
    await state.clear()
    await callback.answer()


# Управление информационными текстами

@router.callback_query(F.data == "admin_info_texts")
async def admin_info_texts_menu(callback: CallbackQuery, config: BotConfig, state: FSMContext):
    """Меню управления информационными текстами"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    await state.clear()
    
    await callback.message.edit_text(
        "📝 <b>Управление текстами кнопок</b>\n\n"
        "Выберите текст для редактирования:",
        reply_markup=get_admin_info_texts_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_info_text_"))
async def admin_info_text_detail(callback: CallbackQuery, config: BotConfig, db: Database):
    """Показать меню действий с текстом"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    text_type = callback.data.split("_")[3]  # rules, guarantees, help
    
    text_names = {
        'rules': '📋 Правила',
        'guarantees': '✅ Гарантии',
        'help': '❓ Помощь'
    }
    
    text_name = text_names.get(text_type, text_type)
    
    await callback.message.edit_text(
        f"📝 <b>{text_name}</b>\n\n"
        f"Выберите действие:",
        reply_markup=get_admin_info_text_actions_keyboard(text_type)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_info_preview_"))
async def admin_info_text_preview(callback: CallbackQuery, config: BotConfig, db: Database, bot):
    """Предпросмотр текста"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    text_type = callback.data.split("_")[3]
    
    text = await db.get_info_text(text_type)
    
    if not text:
        await callback.answer("❌ Текст не установлен", show_alert=True)
        return
    
    # Отправляем предпросмотр отдельным сообщением
    preview_msg = await callback.message.answer(
        f"👁 <b>Предпросмотр:</b>\n\n{text}"
    )
    await callback.answer("✅ Предпросмотр отправлен")
    
    # Автоудаление через 30 секунд
    from ..utils import delete_message_after_delay
    asyncio.create_task(
        delete_message_after_delay(bot, callback.message.chat.id, preview_msg.message_id, 30)
    )


@router.callback_query(F.data.startswith("admin_info_edit_"))
async def admin_info_text_edit_start(callback: CallbackQuery, config: BotConfig, state: FSMContext, db: Database):
    """Начало редактирования текста"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    text_type = callback.data.split("_")[3]
    
    text_names = {
        'rules': '📋 Правила',
        'guarantees': '✅ Гарантии',
        'help': '❓ Помощь'
    }
    
    text_name = text_names.get(text_type, text_type)
    
    # Получаем текущий текст
    current_text = await db.get_info_text(text_type)
    
    message_text = f"✏️ <b>Редактирование: {text_name}</b>\n\n"
    
    if current_text:
        message_text += f"Текущий текст:\n\n{current_text}\n\n"
    
    message_text += "Введите новый текст (поддерживается HTML форматирование):"
    
    msg = await callback.message.edit_text(message_text)
    
    await state.update_data(
        text_type=text_type,
        first_bot_message_id=msg.message_id,
        messages_to_delete=[]
    )
    await state.set_state(EditInfoTextStates.entering_text)
    await callback.answer()


@router.message(EditInfoTextStates.entering_text)
async def admin_info_text_edit_save(message: Message, state: FSMContext, db: Database):
    """Сохранение отредактированного текста"""
    data = await state.get_data()
    text_type = data['text_type']
    
    new_text = message.text
    
    # Сохраняем текст
    await db.set_info_text(text_type, new_text)
    
    text_names = {
        'rules': '📋 Правила',
        'guarantees': '✅ Гарантии',
        'help': '❓ Помощь'
    }
    
    text_name = text_names.get(text_type, text_type)
    
    # Удаляем промежуточные сообщения
    messages_to_delete = data.get('messages_to_delete', [])
    messages_to_delete.append(message.message_id)
    
    for msg_id in messages_to_delete:
        try:
            await message.bot.delete_message(message.chat.id, msg_id)
        except Exception:
            pass
    
    # Редактируем первое сообщение
    first_bot_msg = data.get('first_bot_message_id')
    if first_bot_msg:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=first_bot_msg,
                text=f"✅ Текст '<b>{text_name}</b>' успешно обновлен!\n\n"
                     f"Пользователи теперь будут видеть новый текст.",
                reply_markup=get_admin_info_texts_keyboard()
            )
        except Exception:
            await message.answer(
                f"✅ Текст '<b>{text_name}</b>' успешно обновлен!\n\n"
                f"Пользователи теперь будут видеть новый текст.",
                reply_markup=get_admin_info_texts_keyboard()
            )
    else:
        await message.answer(
            f"✅ Текст '<b>{text_name}</b>' успешно обновлен!\n\n"
            f"Пользователи теперь будут видеть новый текст.",
            reply_markup=get_admin_info_texts_keyboard()
        )
    
    await state.clear()


@router.callback_query(F.data.startswith("admin_info_reset_"))
async def admin_info_text_reset(callback: CallbackQuery, config: BotConfig, db: Database):
    """Сброс текста на дефолтное значение"""
    if not is_admin(callback.from_user.id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    text_type = callback.data.split("_")[3]
    
    default_texts = {
        'rules': (
            "📋 Правила магазина\n\n"
            "1️⃣ Все покупки осуществляются через бота\n"
            "2️⃣ Возврат средств возможен только в случае проблем с товаром\n"
            "3️⃣ Запрещена перепродажа приобретенных товаров\n"
            "4️⃣ При возникновении проблем обращайтесь в поддержку\n"
            "5️⃣ Пополнение баланса происходит в течение 5-15 минут\n\n"
            "⚠️ Администрация оставляет за собой право изменять правила"
        ),
        'guarantees': (
            "✅ Наши гарантии\n\n"
            "🔒 Все товары проверены и работают\n"
            "💎 Гарантия качества на все товары\n"
            "⚡️ Мгновенная выдача после оплаты\n"
            "🔄 Замена нерабочих товаров\n"
            "👨‍💼 Профессиональная поддержка 24/7\n"
            "💯 100% безопасность платежей\n\n"
            "❤️ Мы дорожим каждым клиентом!"
        ),
        'help': (
            "❓ Помощь\n\n"
            "🛒 Как купить товар:\n"
            "1. Пополните баланс\n"
            "2. Выберите товар из каталога\n"
            "3. Подтвердите покупку\n"
            "4. Получите товар мгновенно\n\n"
            "💰 Как пополнить баланс:\n"
            "Нажмите кнопку 'Пополнить баланс' и следуйте инструкциям\n\n"
            "📞 Поддержка:\n"
            "Если у вас возникли вопросы, свяжитесь с администратором"
        )
    }
    
    default_text = default_texts.get(text_type)
    
    if not default_text:
        await callback.answer("❌ Неизвестный тип текста", show_alert=True)
        return
    
    # Сохраняем дефолтный текст
    await db.set_info_text(text_type, default_text)
    
    text_names = {
        'rules': '📋 Правила',
        'guarantees': '✅ Гарантии',
        'help': '❓ Помощь'
    }
    
    text_name = text_names.get(text_type, text_type)
    
    await callback.answer(f"✅ Текст '{text_name}' сброшен на дефолт")
    
    # Возвращаемся к меню действий
    await callback.message.edit_text(
        f"📝 <b>{text_name}</b>\n\n"
        f"Текст сброшен на дефолтное значение.\n"
        f"Выберите действие:",
        reply_markup=get_admin_info_text_actions_keyboard(text_type)
    )

