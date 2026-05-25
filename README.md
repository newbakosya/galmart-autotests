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
│   └── test_smoke.py   # Smoke-тесты (папка 00)
├── config.py            # Конфигурация и URL-хелперы
├── conftest.py          # Фикстуры pytest
├── pytest.ini           # Настройки pytest
└── requirements.txt     # Зависимости
## Запуск тестов
pip install -r requirements.txt
pytest tests/test_smoke.py -v
pytest -v
## Переменные окружения
Создай файл `.env` в корне проекта:
BASE_URL=https://test1.galmart.kz
PHONE=77785636893
CITY_ID=6737
ACCESS_TOKEN=your_token_here
## Покрытие
| Модуль | Тестов | Статус |
|--------|--------|--------|
| Smoke (00) | 5 | ✅ |
| Auth (01) | в разработке | 🔄 |
| Catalog (05) | в разработке | 🔄 |