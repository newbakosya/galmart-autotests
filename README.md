# Galmart API Autotests

Автоматизированное тестирование API мобильного e-commerce приложения Galmart.

## Стек
- Python 3.13
- pytest 7.4
- requests 2.31
- python-dotenv

## Структура проекта

galmart-autotests/
├── tests/
│   ├── test_smoke.py       # Smoke-тесты (папка 00)
│   ├── test_auth.py        # Авторизация (папка 01)
│   ├── test_catalog.py     # Каталог (папка 05)
│   ├── test_profile.py     # Профиль (папка 02)
│   ├── test_cards.py       # Карты (папка 03)
│   ├── test_addresses.py   # Адреса (папка 04)
│   └── test_favorites.py   # Избранное (папка 06)
├── config.py               # Конфигурация и URL-хелперы
├── conftest.py             # Фикстуры pytest
├── pytest.ini              # Настройки pytest
└── requirements.txt        # Зависимости

## Запуск тестов

pip install -r requirements.txt
pytest -v

## Переменные окружения

Создай файл .env в корне проекта:

BASE_URL=https://test1.galmart.kz
CITY_ID=6737
ACCESS_TOKEN=your_token_here

## Покрытие

| Модуль | Тестов | Статус |
|--------|--------|--------|
| Smoke (00) | 5 | ✅ |
| Auth (01) | 11 | ✅ |
| Profile (02) | 13 | ✅ |
| Cards (03) | 8 | ✅ |
| Addresses (04) | 13 | ✅ |
| Catalog (05) | 15 | ✅ |
| Favorites (06) | 8 | ✅ |
| Basket (07) | 🔄 в разработке | |
| Orders (08) | 🔄 в разработке | |
| Promocodes (09) | 🔄 в разработке | |
| Notifications (10) | 🔄 в разработке | |
| Security & IDOR (14) | 🔄 в разработке | |

**Итого: 73 теста · 9 багов найдено**