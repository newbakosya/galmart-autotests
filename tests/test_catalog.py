import requests
import pytest
from config import get_url, CITY_ID, get_auth_headers, get_full_headers


class TestCatalog:
    # тесты каталога — папка 05

    def test_base_sections_returns_list(self):
        # базовые разделы — публичный, city не нужен
        url = get_url("/catalog/base-sections/")
        resp = requests.get(url, headers={"Content-Type": "application/json"})
        assert resp.status_code == 200, f"каталог недоступен, статус: {resp.status_code}"
        data = resp.json()
        assert "data" in data, f"нет поля data, поля: {list(data.keys())}"
        sections = data["data"]
        assert isinstance(sections, list) and len(sections) > 0, "список разделов пустой"
        for s in sections:
            assert "id" in s, f"раздел без id: {s}"

    def test_homepage_structure(self):
        url = get_url("/catalog/homepage/")
        resp = requests.get(url, headers={"Content-Type": "application/json"})
        assert resp.status_code == 200, f"главная недоступна, статус: {resp.status_code}"
        data = resp.json()
        assert data is not None and data != {}, "главная вернула пустой ответ"

    def test_search_goods(self):
        # ищем молоко, нужны авторизация и city
        url = get_url("/catalog/goods/")
        resp = requests.get(url, params={"search": "молоко", "page": 1, "limit": 10}, headers=get_full_headers())
        assert resp.status_code == 200, f"поиск недоступен, статус: {resp.status_code}, ответ: {resp.text[:200]}"
        assert "data" in resp.json(), f"нет поля data, поля: {list(resp.json().keys())}"

    @pytest.mark.parametrize("ordering", ["popular", "price_asc", "price_desc", "name"])
    def test_goods_sorting(self, ordering):
        # проверяем все 4 варианта сортировки
        url = get_url("/catalog/goods/")
        resp = requests.get(url, params={"ordering": ordering, "limit": 5}, headers=get_full_headers())
        assert resp.status_code == 200, f"сортировка '{ordering}' вернула {resp.status_code}"
        assert resp.status_code != 500, f"сортировка '{ordering}' уронила сервер"

    def test_section_goods_without_city_header(self):
        # без city header должна быть ошибка, но апи возвращает 200 — расхождение с доками
        url = get_url("/catalog/goods/")
        resp = requests.get(url, headers={"Content-Type": "application/json"})
        assert resp.status_code != 500, f"сервер упал без city header, ответ: {resp.text[:200]}"
        assert resp.status_code in [200, 400, 401], f"неожиданный статус: {resp.status_code}"

    def test_nonexistent_section(self):
        # несуществующий раздел — 404
        url = get_url("/catalog/sections/999999/goods/")
        resp = requests.get(url, headers={"City": CITY_ID, "Content-Type": "application/json"})
        assert resp.status_code == 404, f"ожидали 404, получили: {resp.status_code}"

    def test_nonexistent_good(self):
        # несуществующий товар — 404
        url = get_url("/catalog/goods/999999999/")
        resp = requests.get(url, headers={"City": CITY_ID, "Content-Type": "application/json"})
        assert resp.status_code == 404, f"ожидали 404, получили: {resp.status_code}"

    def test_page_out_of_range(self):
        # запредельный номер страницы — не должно быть 500
        url = get_url("/catalog/goods/")
        resp = requests.get(url, params={"page": 99999, "limit": 16}, headers={"City": CITY_ID, "Content-Type": "application/json"})
        assert resp.status_code != 500, f"сервер упал на странице 99999, ответ: {resp.text[:200]}"

    def test_sql_injection_in_search(self):
        # sql инъекция — базовая проверка безопасности
        url = get_url("/catalog/goods/")
        resp = requests.get(url, params={"search": "'; DROP TABLE goods; --"}, headers={"City": CITY_ID, "Content-Type": "application/json"})
        assert resp.status_code != 500, f"сервер упал на sql инъекции, ответ: {resp.text[:200]}"

    def test_xss_in_search(self):
        url = get_url("/catalog/goods/")
        resp = requests.get(url, params={"search": "<script>alert(1)</script>"}, headers={"City": CITY_ID, "Content-Type": "application/json"})
        assert resp.status_code != 500, f"сервер упал на xss, ответ: {resp.text[:200]}"

    def test_emoji_in_search(self):
        # казалось бы мелочь, но некоторые бэкенды на эмодзи падают
        url = get_url("/catalog/goods/")
        resp = requests.get(url, params={"search": "🥛🧀"}, headers={"City": CITY_ID, "Content-Type": "application/json"})
        assert resp.status_code != 500, f"сервер упал на эмодзи, ответ: {resp.text[:200]}"

    def test_compilations_available(self):
        # подборки товаров — публичный, city не нужен
        url = get_url("/catalog/compilations/")
        resp = requests.get(url, params={"page": 1, "limit": 10}, headers={"Content-Type": "application/json"})
        assert resp.status_code == 200, f"подборки недоступны, статус: {resp.status_code}"
