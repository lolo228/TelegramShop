<div align="center">

# 🛍️ TelegramShop

### Современный Telegram бот-магазин для продажи цифровых товаров

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![aiogram](https://img.shields.io/badge/aiogram-3.x-blue.svg)](https://docs.aiogram.dev/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[Особенности](#-особенности) • [Установка](#-установка) • [Настройка](#-настройка) • [Запуск](#-запуск) • [Документация](#-структура-проекта)

</div>

---

## 📋 О проекте

**TelegramShop** — это готовое решение для создания магазина цифровых товаров в Telegram. Бот построен на современном стеке технологий с использованием асинхронного программирования и предоставляет все необходимые инструменты для ведения бизнеса в мессенджере.

## ✨ Особенности

<table>
<tr>
<td width="50%">

### 👥 Для пользователей
- ✅ **Проверка подписки** — контроль доступа через канал
- 👤 **Личный профиль** — вся информация о пользователе
- 💰 **Управление балансом** — удобное пополнение счета
- 📦 **История заказов** — отслеживание покупок
- 💳 **История транзакций** — прозрачность операций

</td>
<td width="50%">

### 🔧 Для администраторов
- 🛒 **Управление каталогом** — добавление товаров
- 📊 **Статистика продаж** — аналитика бизнеса
- 👮 **Панель администратора** — полный контроль
- 📋 **Информационные разделы** — правила, гарантии, помощь
- 🔐 **Безопасность** — защита данных пользователей

</td>
</tr>
</table>

## 🚀 Быстрый старт

### Предварительные требования

- Python 3.10 или выше
- Poetry (менеджер зависимостей)
- Telegram Bot Token от [@BotFather](https://t.me/BotFather)

## 📥 Установка

1. **Клонируйте репозиторий:**
```bash
git clone https://github.com/yourusername/TelegramShop.git
cd TelegramShop
```

2. **Установите зависимости:**
```bash
poetry install
```

## ⚙️ Настройка

1. **Создайте файл окружения:**
```bash
cp .env.example .env
```

2. **Настройте переменные окружения в `.env`:**

| Переменная | Описание | Пример |
|------------|----------|--------|
| `BOT_TOKEN` | Токен бота от @BotFather | `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz` |
| `ADMIN_IDS` | ID администраторов (через запятую) | `123456789,987654321` |
| `CHANNEL_ID` | ID или username канала | `@your_channel` |
| `CHANNEL_URL` | Ссылка на канал | `https://t.me/your_channel` |
| `CHECK_SUBSCRIPTION` | Проверка подписки (true/false) | `true` |

<details>
<summary>📝 Как получить ID канала?</summary>

1. Добавьте бота [@userinfobot](https://t.me/userinfobot) в свой канал
2. Перешлите любое сообщение из канала боту
3. Бот покажет ID канала (формат: `-100XXXXXXXXXX`)

</details>

## 🎯 Запуск

Выберите удобный способ запуска:

### Через Poetry (рекомендуется):
```bash
poetry run python -m telegramshop
```

### Через команду:
```bash
poetry install
poetry run telegramshop
```

### Через скрипт:
```bash
python run.py
```

## 📁 Структура проекта

```
TelegramShop/
│
├── 📂 src/
│   └── 📂 telegramshop/
│       ├── 📄 __init__.py
│       ├── 📄 __main__.py       # Точка входа
│       ├── 📄 main.py           # Главный файл приложения
│       ├── 📄 config.py         # Конфигурация и настройки
│       ├── 📄 database.py       # Работа с базой данных
│       ├── 📄 keyboards.py      # Клавиатуры интерфейса
│       │
│       └── 📂 handlers/         # Обработчики событий
│           ├── 📄 __init__.py
│           ├── 📄 start.py      # Команда /start и подписка
│           ├── 📄 profile.py    # Профиль и баланс
│           └── 📄 info.py       # Информационные разделы
│
├── 📂 data/                     # База данных (SQLite)
├── 📄 .env                      # Переменные окружения
├── 📄 .env.example             # Шаблон настроек
├── 📄 run.py                   # Скрипт быстрого запуска
├── 📄 pyproject.toml           # Конфигурация Poetry
└── 📄 README.md                # Документация
```

## 🛠️ Технологический стек

| Технология | Версия | Описание |
|------------|--------|----------|
| ![Python](https://img.shields.io/badge/-Python-3776AB?style=flat&logo=python&logoColor=white) | 3.10+ | Основной язык программирования |
| ![aiogram](https://img.shields.io/badge/-aiogram-26A5E4?style=flat&logo=telegram&logoColor=white) | 3.x | Асинхронный фреймворк для Telegram Bot API |
| ![SQLite](https://img.shields.io/badge/-SQLite-003B57?style=flat&logo=sqlite&logoColor=white) | Latest | Легковесная база данных |
| ![aiosqlite](https://img.shields.io/badge/-aiosqlite-003B57?style=flat) | Latest | Асинхронная работа с SQLite |
| ![python-dotenv](https://img.shields.io/badge/-python--dotenv-ECD53F?style=flat) | Latest | Управление переменными окружения |

## 📚 Основные команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Запуск бота и регистрация |
| `/profile` | Просмотр профиля |
| `/balance` | Управление балансом |
| `/orders` | История заказов |
| `/catalog` | Каталог товаров |
| `/help` | Помощь и поддержка |
</div>

