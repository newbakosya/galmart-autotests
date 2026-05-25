import requests
import pytest
from config import get_url, CITY_ID


class TestSmoke:

    def test_send_code_endpoint_is_alive(self):
        url = get_url("/account/send_code/")
        response = requests.post(
            url,
            json={"login": ""},
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code != 404, \
            f"Эндпоинт не найден (404). URL: {url}"
        assert response.status_code != 500, \
            f"Сервер упал (500). Ответ: {response.text[:300]}"
        assert response.status_code == 400, \
            f"Ожидали 400 на пустой login. Получили: {response.status_code}. Ответ: {response.text[:300]}"

    def test_catalog_base_sections_available(self):
        url = get_url("/catalog/base-sections/")
        response = requests.get(
            url,
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 200, \
            f"Каталог недоступен. Статус: {response.status_code}. Ответ: {response.text[:300]}"
        try:
            data = response.json()
        except Exception as e:
            pytest.fail(f"Ответ не является валидным JSON: {e}")
        assert isinstance(data, dict), \
            f"Ожидали объект (dict). Получили: {type(data).__name__}"
        assert "data" in data, \
            f"В ответе нет поля 'data'. Поля: {list(data.keys())}"
        sections = data["data"]
        assert isinstance(sections, list), \
            f"Поле 'data' должно быть списком. Получили: {type(sections).__name__}"
        assert len(sections) > 0, \
            "Список разделов пустой"
        first_section = sections[0]
        assert "id" in first_section, \
            f"Раздел не содержит поле 'id'. Поля: {list(first_section.keys())}"

    def test_homepage_available(self):
        url = get_url("/catalog/homepage/")
        response = requests.get(
            url,
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 200, \
            f"Главная недоступна. Статус: {response.status_code}. Ответ: {response.text[:300]}"
        try:
            data = response.json()
        except Exception as e:
            pytest.fail(f"Ответ не является валидным JSON: {e}")
        assert data is not None, "Главная вернула null"

    def test_basket_requires_auth(self):
        url = get_url("/orders/basket/")
        response = requests.get(
            url,
            headers={
                "City": CITY_ID,
                "Content-Type": "application/json",
            },
        )
        assert response.status_code != 404, \
            f"Эндпоинт корзины не найден (404). URL: {url}"
        assert response.status_code != 500, \
            f"Сервер упал (500). Ответ: {response.text[:300]}"
        assert response.status_code == 401, \
            f"Ожидали 401 без токена. Получили: {response.status_code}"

    def test_profile_requires_auth(self):
        url = get_url("/account/profile/")
        response = requests.get(
            url,
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 401, \
            f"Профиль доступен без авторизации! Статус: {response.status_code}"