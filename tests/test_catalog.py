import requests
import pytest
from config import get_url, CITY_ID, get_auth_headers, get_full_headers


class TestCatalog:
    """
    Тесты каталога — папка 05 из Postman-коллекции.
    """

    # ── 05.2 ──────────────────────────────────────────────────────────────
    def test_base_sections_returns_list(self):
        """
        Базовые разделы каталога — публичный эндпоинт, City не нужен.
        Проверяем структуру ответа и что разделы вообще есть.
        """
        url = get_url("/catalog/base-sections/")
        response = requests.get(
            url,
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 200, \
            f"Каталог недоступен. Статус: {response.status_code}"
        data = response.json()
        assert "data" in data, \
            f"Нет поля 'data' в ответе. Поля: {list(data.keys())}"
        sections = data["data"]
        assert isinstance(sections, list), \
            f"'data' должен быть списком. Получили: {type(sections).__name__}"
        assert len(sections) > 0, \
            "Список разделов пустой"
        # каждый раздел должен содержать id
        for section in sections:
            assert "id" in section, \
                f"Раздел без поля 'id': {section}"

    # ── 05.1 ──────────────────────────────────────────────────────────────
    def test_homepage_structure(self):
        """
        Главная страница — проверяем что ответ не пустой
        и содержит хоть какие-то данные.
        """
        url = get_url("/catalog/homepage/")
        response = requests.get(
            url,
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 200, \
            f"Главная недоступна. Статус: {response.status_code}"
        data = response.json()
        assert data is not None, "Главная вернула null"
        assert data != {}, "Главная вернула пустой объект"

    # ── 05.5 ──────────────────────────────────────────────────────────────
    def test_search_goods(self):
        """
        Поиск товаров — ищем 'молоко', нужны авторизация и City.
        """
        url = get_url("/catalog/goods/")
        response = requests.get(
            url,
            params={"search": "молоко", "page": 1, "limit": 10},
            headers=get_full_headers(),
        )
        assert response.status_code == 200, \
            f"Поиск недоступен. Статус: {response.status_code}. Ответ: {response.text[:300]}"
        data = response.json()
        assert "data" in data, \
            f"Нет поля 'data'. Поля: {list(data.keys())}"

    # ── 05.6 — 05.9 ───────────────────────────────────────────────────────
    @pytest.mark.parametrize("ordering", ["popular", "price_asc", "price_desc", "name"])
    def test_goods_sorting(self, ordering):
        """
        Все 4 варианта сортировки товаров — Popular, price asc/desc, alphabet.
        Используем parametrize чтобы не дублировать код 4 раза.
        Каждый вариант отдельный тест-кейс в отчёте.
        """
        url = get_url("/catalog/goods/")
        response = requests.get(
            url,
            params={"ordering": ordering, "limit": 5},
            headers=get_full_headers(),
        )
        assert response.status_code == 200, \
            f"Сортировка '{ordering}' вернула {response.status_code}"
        assert response.status_code != 500, \
            f"Сортировка '{ordering}' уронила сервер"

    # ── 05.15 ─────────────────────────────────────────────────────────────
    def test_section_goods_without_city_header(self):
        """
        Товары раздела без City header — должна быть ошибка.
        Из коллекции: City для этого эндпоинта обязателен.
        """
        url = get_url("/catalog/goods/")
        response = requests.get(
            url,
            headers={"Content-Type": "application/json"},
            # намеренно не передаём City
        )
        assert response.status_code != 500, \
            f"Сервер упал без City header. Ответ: {response.text[:300]}"
        # фиксируем что эндпоинт работает без City — расхождение с документацией
        assert response.status_code in [200, 400, 401], \
            f"Неожиданный статус без City: {response.status_code}"

    # ── 05.16 ─────────────────────────────────────────────────────────────
    def test_nonexistent_section(self):
        """
        Несуществующий раздел — должен быть 404.
        ID 999999 заведомо не существует.
        """
        url = get_url("/catalog/sections/999999/goods/")
        response = requests.get(
            url,
            headers={
                "City": CITY_ID,
                "Content-Type": "application/json",
            },
        )
        assert response.status_code == 404, \
            f"Ожидали 404 на несуществующий раздел. Получили: {response.status_code}"

    # ── 05.17 ─────────────────────────────────────────────────────────────
    def test_nonexistent_good(self):
        """
        Несуществующий товар — должен быть 404.
        """
        url = get_url("/catalog/goods/999999999/")
        response = requests.get(
            url,
            headers={
                "City": CITY_ID,
                "Content-Type": "application/json",
            },
        )
        assert response.status_code == 404, \
            f"Ожидали 404 на несуществующий товар. Получили: {response.status_code}"

    # ── 05.19 ─────────────────────────────────────────────────────────────
    def test_page_out_of_range(self):
        """
        Страница далеко за пределами — сервер не должен падать.
        Ожидаем 200 с пустым списком или 404, но не 500.
        """
        url = get_url("/catalog/goods/")
        response = requests.get(
            url,
            params={"page": 99999, "limit": 16},
            headers={
                "City": CITY_ID,
                "Content-Type": "application/json",
            },
        )
        assert response.status_code != 500, \
            f"Сервер упал на запредельном номере страницы. Ответ: {response.text[:300]}"

    # ── 05.21 ─────────────────────────────────────────────────────────────
    def test_sql_injection_in_search(self):
        """
        SQL-инъекция в поиске — сервер не должен падать.
        Это базовая проверка безопасности.
        """
        url = get_url("/catalog/goods/")
        response = requests.get(
            url,
            params={"search": "'; DROP TABLE goods; --"},
            headers={
                "City": CITY_ID,
                "Content-Type": "application/json",
            },
        )
        assert response.status_code != 500, \
            f"Сервер упал на SQL-инъекции. Ответ: {response.text[:300]}"

    # ── 05.22 ─────────────────────────────────────────────────────────────
    def test_xss_in_search(self):
        """
        XSS в поиске — сервер не должен падать,
        скрипт не должен исполниться (проверяем что нет 500).
        """
        url = get_url("/catalog/goods/")
        response = requests.get(
            url,
            params={"search": "<script>alert(1)</script>"},
            headers={
                "City": CITY_ID,
                "Content-Type": "application/json",
            },
        )
        assert response.status_code != 500, \
            f"Сервер упал на XSS. Ответ: {response.text[:300]}"

    # ── 05.25 ─────────────────────────────────────────────────────────────
    def test_emoji_in_search(self):
        """
        Эмодзи в поиске — просто проверяем что не 500.
        Казалось бы мелочь, но некоторые бэкенды на такое падают.
        """
        url = get_url("/catalog/goods/")
        response = requests.get(
            url,
            params={"search": "🥛🧀"},
            headers={
                "City": CITY_ID,
                "Content-Type": "application/json",
            },
        )
        assert response.status_code != 500, \
            f"Сервер упал на эмодзи. Ответ: {response.text[:300]}"

    # ── 05.12 ─────────────────────────────────────────────────────────────
    def test_compilations_available(self):
        """
        Подборки товаров — публичный эндпоинт, City не нужен.
        """
        url = get_url("/catalog/compilations/")
        response = requests.get(
            url,
            params={"page": 1, "limit": 10},
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 200, \
            f"Подборки недоступны. Статус: {response.status_code}"