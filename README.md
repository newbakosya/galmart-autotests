# Galmart API Autotests

Автоматизированное тестирование API мобильного e-commerce приложения Galmart.

## Стек
- Python 3.13
- pytest 7.4
- requests 2.31
- python-dotenv

## Структура проекта

```
galmart-autotests/
├── tests/
│   ├── test_smoke.py          # Smoke-тесты (папка 00)
│   ├── test_auth.py           # Авторизация (папка 01)
│   ├── test_profile.py        # Профиль (папка 02)
│   ├── test_cards.py          # Карты (папка 03)
│   ├── test_addresses.py      # Адреса (папка 04)
│   ├── test_catalog.py        # Каталог (папка 05)
│   ├── test_favorites.py      # Избранное (папка 06)
│   ├── test_basket.py         # Корзина (папка 07)
│   ├── test_orders.py         # Заказы (папка 08)
│   ├── test_promocodes.py     # Промокоды (папка 09)
│   ├── test_notifications.py  # Уведомления (папка 10)
│   ├── test_chat.py           # Чат и поддержка (папка 11)
│   ├── test_actions.py        # Регистрация чека (папка 12)
│   ├── test_references.py     # Справочники (папка 13)
│   ├── test_security.py       # Безопасность и IDOR (папка 14)
│   └── test_bug_probe.py      # Верификация багов (BUG-PROBE)
├── config.py                  # Конфигурация и URL-хелперы
├── conftest.py                # Фикстуры pytest
├── pytest.ini                 # Настройки pytest
└── requirements.txt           # Зависимости
```

## Запуск тестов

```bash
pip install -r requirements.txt
pytest tests/ -v
```

## Переменные окружения

Создай файл `.env` в корне проекта:

```
BASE_URL=https://test1.galmart.kz
CITY_ID=6737
ACCESS_TOKEN=your_token_here
DELIVERY_DATE=2026-06-01
DELIVERY_TIME=10:00 - 12:00
ADDRESS_ID=
CARD_ID=
```

## Покрытие

| Модуль | Тестов | Статус |
|--------|--------|--------|
| Smoke (00) | 5 | ✅ |
| Auth (01) | 11 | ✅ |
| Profile (02) | 12 | ✅ |
| Cards (03) | 8 | ✅ |
| Addresses (04) | 11 | ✅ |
| Catalog (05) | 12 | ✅ |
| Favorites (06) | 8 | ✅ |
| Basket (07) | 12 | ✅ |
| Orders (08) | 15 | ✅ |
| Promocodes (09) | 9 | ✅ |
| Notifications (10) | 12 | ✅ |
| Chat & Support (11) | 5 | ✅ |
| Actions (12) | 8 | ✅ |
| References (13) | 9 | ✅ |
| Security & IDOR (14) | 10 | ✅ |
| BUG-PROBE | 7 | ✅ |

**Итого: 154 теста · 14 багов найдено · 11 xfail на известные баги**

## Результаты последнего прогона

```
148 passed, 1 skipped, 10 xfailed, 1 xpassed in 79.21s
```

Окружение: Stage (test1.galmart.kz) · Python 3.13 · Windows 10 · 28.05.2026