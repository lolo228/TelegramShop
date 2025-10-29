"""
Модуль для работы с базой данных
"""
import aiosqlite
from datetime import datetime
from typing import Optional


class Database:
    """Класс для работы с базой данных"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    async def init_db(self):
        """Инициализация базы данных"""
        async with aiosqlite.connect(self.db_path) as db:
            # Таблица пользователей
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    balance REAL DEFAULT 0,
                    purchases_count INTEGER DEFAULT 0,
                    is_blocked BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица заказов
            await db.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    product_name TEXT,
                    amount REAL,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # Таблица пополнений
            await db.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    amount REAL,
                    status TEXT,
                    payment_method TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # Таблица настроек
            await db.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            
            # Таблица категорий
            await db.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    position INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица товаров
            await db.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL,
                    stock_count INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    position INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories (category_id)
                )
            """)
            
            # Таблица товарных позиций (данные для выдачи)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS product_items (
                    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER,
                    data TEXT NOT NULL,
                    is_sold BOOLEAN DEFAULT 0,
                    sold_to_user_id INTEGER,
                    sold_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (product_id)
                )
            """)
            
            await db.commit()
    
    async def add_user(self, user_id: int, username: Optional[str], first_name: str):
        """Добавление нового пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR IGNORE INTO users (user_id, username, first_name)
                VALUES (?, ?, ?)
            """, (user_id, username, first_name))
            await db.commit()
    
    async def get_user(self, user_id: int):
        """Получение информации о пользователе"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM users WHERE user_id = ?
            """, (user_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    
    async def update_user_balance(self, user_id: int, amount: float):
        """Обновление баланса пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE users SET balance = balance + ? WHERE user_id = ?
            """, (amount, user_id))
            await db.commit()
    
    async def increment_purchases(self, user_id: int):
        """Увеличение счетчика покупок"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE users SET purchases_count = purchases_count + 1 WHERE user_id = ?
            """, (user_id,))
            await db.commit()
    
    async def add_order(self, user_id: int, product_name: str, amount: float, status: str = "completed"):
        """Добавление заказа"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO orders (user_id, product_name, amount, status)
                VALUES (?, ?, ?, ?)
            """, (user_id, product_name, amount, status))
            await db.commit()
    
    async def get_user_orders(self, user_id: int, limit: int = 10):
        """Получение истории заказов пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM orders 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (user_id, limit)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def add_payment(self, user_id: int, amount: float, payment_method: str, status: str = "pending"):
        """Добавление записи о пополнении"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO payments (user_id, amount, payment_method, status)
                VALUES (?, ?, ?, ?)
            """, (user_id, amount, payment_method, status))
            await db.commit()
            return cursor.lastrowid
    
    async def get_user_payments(self, user_id: int, limit: int = 10):
        """Получение истории пополнений пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM payments 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (user_id, limit)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def update_payment_status(self, payment_id: int, status: str):
        """Обновление статуса платежа"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE payments SET status = ? WHERE payment_id = ?
            """, (status, payment_id))
            await db.commit()
    
    async def get_setting(self, key: str) -> Optional[str]:
        """Получение настройки"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT value FROM settings WHERE key = ?
            """, (key,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
    
    async def set_setting(self, key: str, value: str):
        """Установка настройки"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO settings (key, value)
                VALUES (?, ?)
            """, (key, value))
            await db.commit()
    
    # Методы для работы с категориями
    
    async def get_active_categories(self):
        """Получение всех активных категорий"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM categories 
                WHERE is_active = 1 
                ORDER BY position ASC, name ASC
            """) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def get_category(self, category_id: int):
        """Получение категории по ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM categories WHERE category_id = ?
            """, (category_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    
    async def add_category(self, name: str, description: str = "", is_active: bool = True, position: int = 0):
        """Добавление новой категории"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO categories (name, description, is_active, position)
                VALUES (?, ?, ?, ?)
            """, (name, description, is_active, position))
            await db.commit()
            return cursor.lastrowid
    
    async def update_category(self, category_id: int, name: str = None, description: str = None, 
                            is_active: bool = None, position: int = None):
        """Обновление категории"""
        async with aiosqlite.connect(self.db_path) as db:
            fields = []
            values = []
            
            if name is not None:
                fields.append("name = ?")
                values.append(name)
            if description is not None:
                fields.append("description = ?")
                values.append(description)
            if is_active is not None:
                fields.append("is_active = ?")
                values.append(is_active)
            if position is not None:
                fields.append("position = ?")
                values.append(position)
            
            if fields:
                values.append(category_id)
                await db.execute(f"""
                    UPDATE categories SET {', '.join(fields)} WHERE category_id = ?
                """, values)
                await db.commit()
    
    async def delete_category(self, category_id: int):
        """Удаление категории"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM categories WHERE category_id = ?", (category_id,))
            await db.commit()
    
    # Методы для работы с товарами
    
    async def get_products_by_category(self, category_id: int, active_only: bool = True):
        """Получение товаров по категории"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            query = """
                SELECT * FROM products 
                WHERE category_id = ?
            """
            if active_only:
                query += " AND is_active = 1"
            query += " ORDER BY position ASC, name ASC"
            
            async with db.execute(query, (category_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def get_product(self, product_id: int):
        """Получение товара по ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM products WHERE product_id = ?
            """, (product_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    
    async def add_product(self, category_id: int, name: str, description: str, price: float,
                         is_active: bool = True, position: int = 0):
        """Добавление нового товара"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO products (category_id, name, description, price, is_active, position)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (category_id, name, description, price, is_active, position))
            await db.commit()
            return cursor.lastrowid
    
    async def update_product(self, product_id: int, **kwargs):
        """Обновление товара"""
        async with aiosqlite.connect(self.db_path) as db:
            fields = []
            values = []
            
            for key, value in kwargs.items():
                if value is not None and key in ['category_id', 'name', 'description', 'price', 
                                                   'is_active', 'position']:
                    fields.append(f"{key} = ?")
                    values.append(value)
            
            if fields:
                values.append(product_id)
                await db.execute(f"""
                    UPDATE products SET {', '.join(fields)} WHERE product_id = ?
                """, values)
                await db.commit()
    
    async def delete_product(self, product_id: int):
        """Удаление товара"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
            await db.commit()
    
    async def update_product_stock(self, product_id: int):
        """Обновление количества товара в наличии"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE products 
                SET stock_count = (
                    SELECT COUNT(*) FROM product_items 
                    WHERE product_id = ? AND is_sold = 0
                )
                WHERE product_id = ?
            """, (product_id, product_id))
            await db.commit()
    
    # Методы для работы с товарными позициями
    
    async def add_product_item(self, product_id: int, data: str):
        """Добавление товарной позиции"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO product_items (product_id, data)
                VALUES (?, ?)
            """, (product_id, data))
            await db.commit()
            item_id = cursor.lastrowid
            
        # Обновляем количество товара
        await self.update_product_stock(product_id)
        return item_id
    
    async def get_available_product_item(self, product_id: int):
        """Получение доступной товарной позиции"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM product_items 
                WHERE product_id = ? AND is_sold = 0
                LIMIT 1
            """, (product_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    
    async def mark_item_as_sold(self, item_id: int, user_id: int):
        """Отметить товар как проданный"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE product_items 
                SET is_sold = 1, sold_to_user_id = ?, sold_at = CURRENT_TIMESTAMP
                WHERE item_id = ?
            """, (user_id, item_id))
            await db.commit()
    
    # Методы для админки
    
    async def get_all_users(self, limit: int = 50, offset: int = 0):
        """Получение всех пользователей с пагинацией"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM users 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            """, (limit, offset)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def get_users_count(self):
        """Получение общего количества пользователей"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0
    
    async def search_users(self, query: str):
        """Поиск пользователей по ID или username"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # Проверяем, является ли query числом (поиск по ID)
            if query.isdigit():
                async with db.execute("""
                    SELECT * FROM users WHERE user_id = ?
                """, (int(query),)) as cursor:
                    rows = await cursor.fetchall()
            else:
                # Поиск по username
                async with db.execute("""
                    SELECT * FROM users 
                    WHERE username LIKE ? OR first_name LIKE ?
                """, (f"%{query}%", f"%{query}%")) as cursor:
                    rows = await cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    async def set_user_blocked(self, user_id: int, is_blocked: bool):
        """Блокировка/разблокировка пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE users SET is_blocked = ? WHERE user_id = ?
            """, (is_blocked, user_id))
            await db.commit()
    
    async def get_statistics(self):
        """Получение общей статистики"""
        async with aiosqlite.connect(self.db_path) as db:
            # Количество пользователей
            async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                users_count = (await cursor.fetchone())[0]
            
            # Количество продаж
            async with db.execute("SELECT COUNT(*) FROM orders WHERE status = 'completed'") as cursor:
                orders_count = (await cursor.fetchone())[0]
            
            # Общая выручка
            async with db.execute("SELECT SUM(amount) FROM orders WHERE status = 'completed'") as cursor:
                revenue = (await cursor.fetchone())[0] or 0
            
            # Количество активных категорий
            async with db.execute("SELECT COUNT(*) FROM categories WHERE is_active = 1") as cursor:
                active_categories = (await cursor.fetchone())[0]
            
            # Количество активных товаров
            async with db.execute("SELECT COUNT(*) FROM products WHERE is_active = 1") as cursor:
                active_products = (await cursor.fetchone())[0]
            
            # Общее количество товарных позиций в наличии
            async with db.execute("SELECT COUNT(*) FROM product_items WHERE is_sold = 0") as cursor:
                items_in_stock = (await cursor.fetchone())[0]
            
            return {
                'users_count': users_count,
                'orders_count': orders_count,
                'revenue': revenue,
                'active_categories': active_categories,
                'active_products': active_products,
                'items_in_stock': items_in_stock
            }
    
    async def get_all_categories(self, limit: int = 100, offset: int = 0):
        """Получение всех категорий (включая неактивные)"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM categories 
                ORDER BY position ASC, name ASC
                LIMIT ? OFFSET ?
            """, (limit, offset)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def get_all_products(self, limit: int = 100, offset: int = 0):
        """Получение всех товаров (включая неактивные)"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT p.*, c.name as category_name 
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                ORDER BY p.position ASC, p.name ASC
                LIMIT ? OFFSET ?
            """, (limit, offset)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def add_product_items_bulk(self, product_id: int, items_list: list):
        """Массовая загрузка товарных позиций"""
        async with aiosqlite.connect(self.db_path) as db:
            for item_data in items_list:
                await db.execute("""
                    INSERT INTO product_items (product_id, data)
                    VALUES (?, ?)
                """, (product_id, item_data.strip()))
            await db.commit()
        
        # Обновляем количество товара
        await self.update_product_stock(product_id)
        return len(items_list)
    
    # Методы для работы с информационными текстами
    
    async def get_info_text(self, key: str) -> Optional[str]:
        """Получение информационного текста"""
        return await self.get_setting(f"info_{key}")
    
    async def set_info_text(self, key: str, value: str):
        """Установка информационного текста"""
        await self.set_setting(f"info_{key}", value)
    
    async def init_default_info_texts(self):
        """Инициализация дефолтных информационных текстов"""
        # Дефолтные тексты
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
        
        # Устанавливаем тексты только если их еще нет
        for key, default_text in default_texts.items():
            existing_text = await self.get_info_text(key)
            if not existing_text:
                await self.set_info_text(key, default_text)

