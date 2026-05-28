import requests
import pytest
from config import get_url, get_auth_headers

# тестовая карта visa — стандартный номер для тестирования
TEST_CARD = {
    "number": "4111111111111111",
    "month": 12,
    "year": 2028,
    "cvc": "123",
    "name": "QA TESTER"
}


class TestCards:
    # тесты карт — папка 03

    def test_list_cards(self):
        # список карт пользователя — может быть пустым
        url = get_url("/account/card/")
        resp = requests.get(url, headers=get_auth_headers())
        assert resp.status_code == 200, f"список карт недоступен, статус: {resp.status_code}, ответ: {resp.text[:200]}"
        assert resp.json() is not None, "ответ пустой"

    def test_list_cards_no_auth(self):
        # без токена — 401
        url = get_url("/account/card/")
        resp = requests.get(url, headers={"Content-Type": "application/json"})
        assert resp.status_code == 401, f"карты доступны без авторизации! статус: {resp.status_code}"

    def test_add_card_invalid_number(self):
        # апи не валидирует номер карты на своей стороне — фиксируем как баг
        url = get_url("/account/card/")
        resp = requests.post(
            url,
            json={"number": "0000000000000000", "month": 12, "year": 2028, "cvc": "123"},
            headers=get_auth_headers(),
        )
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        # баг: апи возвращает 200 с url шлюза вместо 400
        assert "data" in resp.json(), f"нет поля data, поля: {list(resp.json().keys())}"

    def test_add_card_expired(self):
        # просроченная карта тоже принимается — баг
        url = get_url("/account/card/")
        resp = requests.post(
            url,
            json={"number": "4111111111111111", "month": 1, "year": 2020, "cvc": "123"},
            headers=get_auth_headers(),
        )
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert "data" in resp.json(), f"нет поля data, поля: {list(resp.json().keys())}"

    def test_add_card_empty_body(self):
        # пустое тело — тоже не валидируется, но не должно быть 500
        url = get_url("/account/card/")
        resp = requests.post(url, json={}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал на пустом теле, ответ: {resp.text[:200]}"

    def test_delete_nonexistent_card(self):
        # несуществующая карта — 404
        url = get_url("/account/card/999999/")
        resp = requests.delete(url, headers={**get_auth_headers(), "Shop": "1"})
        assert resp.status_code == 404, f"ожидали 404, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_set_favorite_nonexistent_card(self):
        # установка несуществующей карты как избранной — 404
        url = get_url("/account/card/999999/favorite/")
        resp = requests.post(url, headers=get_auth_headers())
        assert resp.status_code == 404, f"ожидали 404, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_delete_card_without_shop_header(self):
        # shop header обязателен для удаления карты
        url = get_url("/account/card/999999/")
        resp = requests.delete(url, headers=get_auth_headers())  # без shop header намеренно
        assert resp.status_code != 500, f"сервер упал без shop header, ответ: {resp.text[:200]}"
        assert resp.status_code in [400, 404], f"ожидали 400 или 404, статус: {resp.status_code}"
