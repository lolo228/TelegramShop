"""
Модуль с клавиатурами бота
"""
from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Главная reply клавиатура"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🛒 Купить товар"),
                KeyboardButton(text="💰 Пополнить баланс")
            ],
            [
                KeyboardButton(text="👤 Профиль")
            ],
            [
                KeyboardButton(text="📋 Правила"),
                KeyboardButton(text="✅ Гарантии"),
                KeyboardButton(text="❓ Помощь")
            ]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_subscription_keyboard(channel_url: str) -> InlineKeyboardMarkup:
    """Клавиатура для проверки подписки на канал"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📢 Подписаться",
                    url=channel_url
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Проверить",
                    callback_data="check_subscription"
                )
            ]
        ]
    )
    return keyboard


def get_profile_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура профиля"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📦 История заказов",
                    callback_data="order_history"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💰 Пополнить баланс",
                    callback_data="add_balance"
                ),
                InlineKeyboardButton(
                    text="💳 История пополнений",
                    callback_data="payment_history"
                )
            ]
        ]
    )
    return keyboard


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой назад"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="◀️ Назад",
                    callback_data="back_to_profile"
                )
            ]
        ]
    )
    return keyboard


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой отмены"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Отменить",
                    callback_data="cancel"
                )
            ]
        ]
    )
    return keyboard


def get_categories_keyboard(categories: list) -> InlineKeyboardMarkup:
    """Клавиатура с категориями товаров"""
    buttons = []
    
    for category in categories:
        buttons.append([
            InlineKeyboardButton(
                text=category['name'],
                callback_data=f"category_{category['category_id']}"
            )
        ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_products_keyboard(products: list, category_id: int) -> InlineKeyboardMarkup:
    """Клавиатура с товарами категории"""
    buttons = []
    
    for product in products:
        stock_emoji = "✅" if product['stock_count'] > 0 else "❌"
        buttons.append([
            InlineKeyboardButton(
                text=f"{stock_emoji} {product['name']} - {product['price']} руб. (в наличии: {product['stock_count']})",
                callback_data=f"product_{product['product_id']}"
            )
        ])
    
    # Кнопка назад к категориям
    buttons.append([
        InlineKeyboardButton(
            text="◀️ Назад к категориям",
            callback_data="back_to_categories"
        )
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_product_detail_keyboard(product_id: int, category_id: int, in_stock: bool) -> InlineKeyboardMarkup:
    """Клавиатура с действиями для товара"""
    buttons = []
    
    if in_stock:
        buttons.append([
            InlineKeyboardButton(
                text="🛒 Купить",
                callback_data=f"buy_{product_id}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(
            text="◀️ Назад к товарам",
            callback_data=f"category_{category_id}"
        )
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


# Админ клавиатуры

def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    """Главное меню админки"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📦 Управление товарами",
                    callback_data="admin_products"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👥 Управление пользователями",
                    callback_data="admin_users"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Статистика",
                    callback_data="admin_stats"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📢 Рассылка",
                    callback_data="admin_broadcast"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📝 Тексты кнопок",
                    callback_data="admin_info_texts"
                )
            ]
        ]
    )
    return keyboard


def get_admin_products_keyboard() -> InlineKeyboardMarkup:
    """Меню управления товарами"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📂 Категории",
                    callback_data="admin_categories_list"
                ),
                InlineKeyboardButton(
                    text="📦 Товары",
                    callback_data="admin_products_list"
                )
            ],
            [
                InlineKeyboardButton(
                    text="➕ Добавить категорию",
                    callback_data="admin_add_category"
                )
            ],
            [
                InlineKeyboardButton(
                    text="➕ Добавить товар",
                    callback_data="admin_add_product"
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
    return keyboard


def get_admin_categories_list_keyboard(categories: list, page: int = 0) -> InlineKeyboardMarkup:
    """Список категорий для админа"""
    buttons = []
    
    for category in categories:
        status = "✅" if category['is_active'] else "❌"
        buttons.append([
            InlineKeyboardButton(
                text=f"{status} {category['name']}",
                callback_data=f"admin_category_{category['category_id']}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(
            text="◀️ Назад",
            callback_data="admin_products"
        )
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_admin_category_actions_keyboard(category_id: int, is_active: bool) -> InlineKeyboardMarkup:
    """Действия с категорией"""
    toggle_text = "❌ Деактивировать" if is_active else "✅ Активировать"
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Редактировать",
                    callback_data=f"admin_edit_category_{category_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text=toggle_text,
                    callback_data=f"admin_toggle_category_{category_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗑 Удалить",
                    callback_data=f"admin_delete_category_{category_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ Назад к списку",
                    callback_data="admin_categories_list"
                )
            ]
        ]
    )
    return keyboard


def get_admin_products_list_keyboard(products: list) -> InlineKeyboardMarkup:
    """Список товаров для админа"""
    buttons = []
    
    for product in products:
        status = "✅" if product['is_active'] else "❌"
        category_name = product.get('category_name', 'Без категории')
        buttons.append([
            InlineKeyboardButton(
                text=f"{status} {product['name']} ({category_name}) - {product['price']}₽",
                callback_data=f"admin_product_{product['product_id']}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(
            text="◀️ Назад",
            callback_data="admin_products"
        )
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_admin_product_actions_keyboard(product_id: int, is_active: bool) -> InlineKeyboardMarkup:
    """Действия с товаром"""
    toggle_text = "❌ Деактивировать" if is_active else "✅ Активировать"
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Редактировать",
                    callback_data=f"admin_edit_product_{product_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📥 Загрузить позиции",
                    callback_data=f"admin_load_items_{product_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text=toggle_text,
                    callback_data=f"admin_toggle_product_{product_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗑 Удалить",
                    callback_data=f"admin_delete_product_{product_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ Назад к списку",
                    callback_data="admin_products_list"
                )
            ]
        ]
    )
    return keyboard


def get_admin_users_keyboard() -> InlineKeyboardMarkup:
    """Меню управления пользователями"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📋 Список пользователей",
                    callback_data="admin_users_list_0"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔍 Найти пользователя",
                    callback_data="admin_search_user"
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
    return keyboard


def get_admin_users_list_keyboard(users: list, page: int = 0, total_pages: int = 1) -> InlineKeyboardMarkup:
    """Список пользователей с пагинацией"""
    buttons = []
    
    for user in users:
        status = "🚫" if user.get('is_blocked') else "✅"
        username = f"@{user['username']}" if user.get('username') else user['first_name']
        buttons.append([
            InlineKeyboardButton(
                text=f"{status} {username} (ID: {user['user_id']}) - {user['balance']}₽",
                callback_data=f"admin_user_{user['user_id']}"
            )
        ])
    
    # Пагинация
    pagination = []
    if page > 0:
        pagination.append(
            InlineKeyboardButton(
                text="◀️ Назад",
                callback_data=f"admin_users_list_{page - 1}"
            )
        )
    if page < total_pages - 1:
        pagination.append(
            InlineKeyboardButton(
                text="Вперед ▶️",
                callback_data=f"admin_users_list_{page + 1}"
            )
        )
    
    if pagination:
        buttons.append(pagination)
    
    buttons.append([
        InlineKeyboardButton(
            text="◀️ Назад",
            callback_data="admin_users"
        )
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_admin_user_actions_keyboard(user_id: int, is_blocked: bool) -> InlineKeyboardMarkup:
    """Действия с пользователем"""
    block_text = "✅ Разблокировать" if is_blocked else "🚫 Заблокировать"
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💰 Изменить баланс",
                    callback_data=f"admin_change_balance_{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text=block_text,
                    callback_data=f"admin_toggle_block_{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ Назад к списку",
                    callback_data="admin_users_list_0"
                )
            ]
        ]
    )
    return keyboard


def get_broadcast_confirm_keyboard() -> InlineKeyboardMarkup:
    """Подтверждение рассылки"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить и отправить",
                    callback_data="admin_broadcast_confirm"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отменить",
                    callback_data="admin_broadcast_cancel"
                )
            ]
        ]
    )
    return keyboard


def get_admin_select_category_keyboard(categories: list) -> InlineKeyboardMarkup:
    """Выбор категории для товара"""
    buttons = []
    
    for category in categories:
        buttons.append([
            InlineKeyboardButton(
                text=category['name'],
                callback_data=f"admin_select_cat_{category['category_id']}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(
            text="❌ Отменить",
            callback_data="admin_products"
        )
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_admin_info_texts_keyboard() -> InlineKeyboardMarkup:
    """Меню управления информационными текстами"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📋 Правила",
                    callback_data="admin_info_text_rules"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Гарантии",
                    callback_data="admin_info_text_guarantees"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❓ Помощь",
                    callback_data="admin_info_text_help"
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
    return keyboard


def get_admin_info_text_actions_keyboard(text_type: str) -> InlineKeyboardMarkup:
    """Действия с информационным текстом"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👁 Предпросмотр",
                    callback_data=f"admin_info_preview_{text_type}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✏️ Редактировать",
                    callback_data=f"admin_info_edit_{text_type}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Сбросить на дефолт",
                    callback_data=f"admin_info_reset_{text_type}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ Назад",
                    callback_data="admin_info_texts"
                )
            ]
        ]
    )
    return keyboard


def get_edit_category_fields_keyboard(category_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора поля категории для редактирования"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📝 Изменить название",
                    callback_data=f"admin_edit_cat_name_{category_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📄 Изменить описание",
                    callback_data=f"admin_edit_cat_desc_{category_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ Назад",
                    callback_data=f"admin_category_{category_id}"
                )
            ]
        ]
    )
    return keyboard


def get_edit_product_fields_keyboard(product_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора поля товара для редактирования"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📝 Изменить название",
                    callback_data=f"admin_edit_prod_name_{product_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📄 Изменить описание",
                    callback_data=f"admin_edit_prod_desc_{product_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💰 Изменить цену",
                    callback_data=f"admin_edit_prod_price_{product_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ Назад",
                    callback_data=f"admin_product_{product_id}"
                )
            ]
        ]
    )
    return keyboard