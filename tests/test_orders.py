import requests
import pytest
from config import get_url, get_auth_headers, get_full_headers, CITY_ID
import os
from dotenv import load_dotenv
load_dotenv()

_DELIVERY_DATE = os.getenv("DELIVERY_DATE", "2026-06-01")
_DELIVERY_TIME = os.getenv("DELIVERY_TIME", "10:00 - 12:00")
_ADDRESS_ID = os.getenv("ADDRESS_ID", "")
_CARD_ID = os.getenv("CARD_ID", "")

BASE_ORDER_BODY = {
    "address": _ADDRESS_ID,
    "delivery_date": _DELIVERY_DATE,
    "delivery_time": _DELIVERY_TIME,
    "card": _CARD_ID,
    "notes": "QA автотест",
    "bonuses": 0,
    "leave_at_door": False,
    "replace_items_action": "call",
    "allow_unavailable_items": True,
}


class TestOrders:
    # тесты заказов — папка 08

    def test_order_list(self):
        # список заказов — пустой список тоже норм
        url = get_url("/orders/order/")
        resp = requests.get(url, params={"page": 1}, headers=get_auth_headers())
        assert resp.status_code == 200, f"список заказов недоступен, статус: {resp.status_code}, ответ: {resp.text[:200]}"
        assert "data" in resp.json(), f"нет поля data, ответ: {resp.text[:200]}"

    def test_active_orders(self):
        url = get_url("/orders/order/active/")
        resp = requests.get(url, params={"page": 1}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code == 200, f"активные заказы недоступны, статус: {resp.status_code}"

    def test_order_history(self):
        url = get_url("/orders/order/history/")
        resp = requests.get(url, params={"page": 1}, headers=get_auth_headers())
        assert resp.status_code == 200, f"история недоступна, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_review_items(self):
        # товары для ревью — пустой список ок
        url = get_url("/orders/order/review_items/")
        resp = requests.get(url, params={"page": 1}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code == 200, f"review items недоступны, статус: {resp.status_code}"

    def test_create_order_no_auth(self):
        url = get_url("/orders/order/")
        resp = requests.post(url, json=BASE_ORDER_BODY, headers={"Content-Type": "application/json"})
        assert resp.status_code == 401, f"заказ создан без авторизации! статус: {resp.status_code}"

    def test_create_order_no_address(self):
        # без адреса — 400
        url = get_url("/orders/order/")
        resp = requests.post(url, json={"delivery_date": _DELIVERY_DATE, "delivery_time": _DELIVERY_TIME}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code == 400, f"заказ без адреса принят! статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_create_order_past_date(self):
        # дата в прошлом — 400 или 422
        url = get_url("/orders/order/")
        resp = requests.post(url, json={**BASE_ORDER_BODY, "delivery_date": "2020-01-01"}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал на прошедшей дате, ответ: {resp.text[:200]}"
        assert resp.status_code in [400, 422], f"заказ с датой в прошлом принят! статус: {resp.status_code}"

    def test_create_order_invalid_payment_type(self):
        url = get_url("/orders/order/")
        resp = requests.post(url, json={**BASE_ORDER_BODY, "payment_type": "bitcoin"}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code in [400, 422], f"невалидный payment_type принят, статус: {resp.status_code}"

    def test_get_nonexistent_order(self):
        url = get_url("/orders/order/999999/")
        resp = requests.get(url, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code == 404, f"ожидали 404, статус: {resp.status_code}"

    def test_idor_get_other_user_order(self):
        # idor: чужой заказ — 404
        url = get_url("/orders/order/99999/")
        resp = requests.get(url, headers=get_auth_headers())
        assert resp.status_code == 404, f"idor! чужой заказ доступен, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_orders_by_date_invalid_format(self):
        # dd-mm-yyyy вместо yyyy-mm-dd — 400 или 404
        url = get_url("/orders/order/by-date/13-05-2026/")
        resp = requests.get(url, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал на невалидном формате даты, ответ: {resp.text[:200]}"
        assert resp.status_code in [400, 404], f"невалидный формат принят, статус: {resp.status_code}"

    def test_invalid_order_action(self):
        url = get_url("/orders/order/999999/action/")
        resp = requests.post(url, json={"action": "fly_to_moon"}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code in [400, 404, 422], f"невалидный action принят, статус: {resp.status_code}"

    def test_merge_orders_no_guest_token(self):
        url = get_url("/orders/order/merge/")
        resp = requests.post(url, json={"guest_token": ""}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code in [200, 400], f"неожиданный статус: {resp.status_code}"

    def test_xss_in_order_notes(self):
        # xss в notes — скрипт не должен вернуться в ответе
        url = get_url("/orders/order/")
        resp = requests.post(url, json={**BASE_ORDER_BODY, "notes": "<script>alert('xss')</script>"}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert "<script>alert" not in resp.text, "xss не санитизирован — скрипт вернулся в ответе!"

    def test_orders_by_valid_date_format(self):
        # правильный формат yyyy-mm-dd — не 500, пустой результат ок
        url = get_url(f"/orders/order/by-date/{_DELIVERY_DATE}/")
        resp = requests.get(url, params={"page": 1}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code in [200, 404], f"неожиданный статус: {resp.status_code}"
