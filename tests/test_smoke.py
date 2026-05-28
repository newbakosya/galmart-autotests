import requests
import pytest
from config import get_url, CITY_ID


class TestSmoke:

    def test_send_code_endpoint_is_alive(self):
        # просто проверяем что сервер живой
        # пустой логин даст 400, если rate limit — 429, оба варианта норм
        url = get_url("/account/send_code/")
        resp = requests.post(url, json={"login": ""}, headers={"Content-Type": "application/json"})
        assert resp.status_code in [400, 429], f"неожиданный статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_catalog_base_sections_available(self):
        # базовые разделы — публичный эндпоинт, авторизация не нужна
        url = get_url("/catalog/base-sections/")
        resp = requests.get(url, headers={"Content-Type": "application/json"})
        assert resp.status_code == 200, f"каталог недоступен, статус: {resp.status_code}"
        try:
            data = resp.json()
        except Exception as e:
            pytest.fail(f"ответ не json: {e}")
        assert isinstance(data, dict), f"ожидали dict, получили {type(data).__name__}"
        assert "data" in data, f"нет поля data, поля: {list(data.keys())}"
        sections = data["data"]
        assert isinstance(sections, list) and len(sections) > 0, "список разделов пустой"
        assert "id" in sections[0], f"у раздела нет id, поля: {list(sections[0].keys())}"

    def test_homepage_available(self):
        url = get_url("/catalog/homepage/")
        resp = requests.get(url, headers={"Content-Type": "application/json"})
        assert resp.status_code == 200, f"главная недоступна, статус: {resp.status_code}"
        try:
            data = resp.json()
        except Exception as e:
            pytest.fail(f"ответ не json: {e}")
        assert data is not None, "главная вернула null"

    def test_basket_requires_auth(self):
        # корзина без токена должна возвращать 401
        url = get_url("/orders/basket/")
        resp = requests.get(url, headers={"City": CITY_ID, "Content-Type": "application/json"})
        assert resp.status_code != 404, f"эндпоинт корзины не найден, url: {url}"
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code == 401, f"ожидали 401 без токена, получили: {resp.status_code}"

    def test_profile_requires_auth(self):
        url = get_url("/account/profile/")
        resp = requests.get(url, headers={"Content-Type": "application/json"})
        assert resp.status_code == 401, f"профиль доступен без авторизации! статус: {resp.status_code}"
