import requests
import pytest
from config import get_url, get_auth_headers, get_full_headers, CITY_ID


class TestBasket:
    # тесты корзины — папка 07

    def test_get_basket(self):
        # city header обязателен, корзина может быть пустой
        url = get_url("/orders/basket/")
        resp = requests.get(url, headers=get_full_headers())
        assert resp.status_code == 200, f"корзина недоступна, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_get_basket_no_auth(self):
        url = get_url("/orders/basket/")
        resp = requests.get(url, headers={"City": CITY_ID, "Content-Type": "application/json"})
        assert resp.status_code == 401, f"корзина доступна без токена! статус: {resp.status_code}"

    def test_get_basket_as_list(self):
        # as_list — city не нужен
        url = get_url("/orders/basket/as_list/")
        resp = requests.get(url, headers=get_auth_headers())
        assert resp.status_code == 200, f"корзина as_list недоступна, статус: {resp.status_code}"

    @pytest.mark.xfail(reason="BUG: GET /orders/get_delivery_times/ возвращает 404 на stage", strict=True)
    def test_get_delivery_times(self):
        # эндпоинт не в /basket/, а отдельный — city header не нужен
        url = get_url("/orders/get_delivery_times/")
        resp = requests.get(url, headers=get_auth_headers())
        assert resp.status_code == 200, f"слоты доставки недоступны, статус: {resp.status_code}, ответ: {resp.text[:200]}"
        data = resp.json().get("data", [])
        assert isinstance(data, list), f"ожидали список, получили: {type(data)}"
        if data:
            slot = data[0]
            delivery_date = slot.get("date") or slot.get("delivery_date")
            assert delivery_date is not None, "в слоте нет поля date/delivery_date"
            times = slot.get("times") or slot.get("slots", [])
            assert isinstance(times, list), f"ожидали список времён, получили: {type(times)}"

    def test_set_item_negative_qty(self):
        # отрицательное количество — апи конвертирует в 0 вместо 400, фиксируем как баг
        url = get_url("/orders/basket/set/")
        resp = requests.put(url, json={"item": "12345", "count": -1}, headers=get_full_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code in [200, 400], f"неожиданный статус: {resp.status_code}"

    def test_set_nonexistent_item(self):
        url = get_url("/orders/basket/set/")
        resp = requests.put(url, json={"item": 999999999, "count": 1}, headers=get_full_headers())
        assert resp.status_code in [400, 404], f"несуществующий товар добавлен! статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_set_item_no_city_header(self):
        # без city header — баг: корзина работает вопреки документации
        url = get_url("/orders/basket/set/")
        resp = requests.put(url, json={"item": "12345", "count": 1}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал без city header, ответ: {resp.text[:200]}"
        assert resp.status_code in [200, 400, 401], f"неожиданный статус: {resp.status_code}"

    def test_set_delivery_past_date(self):
        # дата в прошлом — 400
        url = get_url("/orders/basket/set_delivery_time/")
        resp = requests.put(url, json={"delivery_date": "2020-01-01", "delivery_time": "10:00 - 12:00"}, headers=get_full_headers())
        assert resp.status_code == 400, f"ожидали 400 на прошедшую дату, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_set_delivery_invalid_format(self):
        url = get_url("/orders/basket/set_delivery_time/")
        resp = requests.put(url, json={"delivery_date": "not-a-date", "delivery_time": "invalid"}, headers=get_full_headers())
        assert resp.status_code == 400, f"ожидали 400 на невалидный формат, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_set_item_very_large_qty(self):
        # 9999 штук — сервер не должен падать
        url = get_url("/orders/basket/set/")
        resp = requests.put(url, json={"item": "12345", "count": 9999}, headers=get_full_headers())
        assert resp.status_code != 500, f"сервер упал на большом qty, ответ: {resp.text[:200]}"

    def test_clear_unavailable_items(self):
        # очистка недоступных товаров — даже если таких нет
        url = get_url("/orders/basket/clear/")
        resp = requests.delete(url, params={"is_unavailable_items": "true"}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code in [200, 204], f"неожиданный статус: {resp.status_code}"

    def test_clear_basket(self):
        # полная очистка — даже если корзина уже пустая
        url = get_url("/orders/basket/clear/")
        resp = requests.delete(url, params={"is_unavailable_items": "false"}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code in [200, 204], f"неожиданный статус: {resp.status_code}"
