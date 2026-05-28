import requests
import pytest
from config import get_url, get_auth_headers, get_full_headers, CITY_ID
import os
from dotenv import load_dotenv
load_dotenv()

_DELIVERY_DATE = os.getenv("DELIVERY_DATE", "2026-06-01")
_DELIVERY_TIME = os.getenv("DELIVERY_TIME", "10:00 - 12:00")
_ADDRESS_ID    = os.getenv("ADDRESS_ID", "")
_CARD_ID       = os.getenv("CARD_ID", "")

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

    # ── 08.4 ──────────────────────────────────────────────────────────────
    def test_order_list(self):
        """
        Список заказов — должен быть доступен всегда.
        Пустой список — нормально.
        """
        url = get_url("/orders/order/")
        response = requests.get(url, params={"page": 1}, headers=get_auth_headers())

        assert response.status_code == 200, \
            f"Список заказов недоступен. Статус: {response.status_code}. Ответ: {response.text[:300]}"
        assert "data" in response.json(), \
            f"Нет поля 'data' в ответе. Ответ: {response.text[:300]}"

    # ── 08.5 ──────────────────────────────────────────────────────────────
    def test_active_orders(self):
        """
        Активные заказы — может быть пустым, главное не 500.
        """
        url = get_url("/orders/order/active/")
        response = requests.get(url, params={"page": 1}, headers=get_auth_headers())

        assert response.status_code != 500, \
            f"Сервер упал. Ответ: {response.text[:300]}"
        assert response.status_code == 200, \
            f"Активные заказы недоступны. Статус: {response.status_code}"

    # ── 08.6 ──────────────────────────────────────────────────────────────
    def test_order_history(self):
        """
        История заказов — пагинация page=1, ответ 200.
        """
        url = get_url("/orders/order/history/")
        response = requests.get(url, params={"page": 1}, headers=get_auth_headers())

        assert response.status_code == 200, \
            f"История заказов недоступна. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 08.8 ──────────────────────────────────────────────────────────────
    def test_review_items(self):
        """
        Товары для ревью — пустой список ок.
        """
        url = get_url("/orders/order/review_items/")
        response = requests.get(url, params={"page": 1}, headers=get_auth_headers())

        assert response.status_code != 500, \
            f"Сервер упал. Ответ: {response.text[:300]}"
        assert response.status_code == 200, \
            f"Review items недоступны. Статус: {response.status_code}"

    # ── 08.18 ─────────────────────────────────────────────────────────────
    def test_create_order_no_auth(self):
        """
        Создание заказа без авторизации → 401.
        """
        url = get_url("/orders/order/")
        response = requests.post(
            url,
            json=BASE_ORDER_BODY,
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 401, \
            f"Заказ создан без авторизации! Статус: {response.status_code}"

    # ── 08.15 ─────────────────────────────────────────────────────────────
    def test_create_order_no_address(self):
        """
        Создание заказа без адреса → 400.
        """
        url = get_url("/orders/order/")
        body = {
            "delivery_date": _DELIVERY_DATE,
            "delivery_time": _DELIVERY_TIME,
        }
        response = requests.post(url, json=body, headers=get_auth_headers())

        assert response.status_code != 500, \
            f"Сервер упал. Ответ: {response.text[:300]}"
        assert response.status_code == 400, \
            f"Заказ без адреса принят! Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 08.17 ─────────────────────────────────────────────────────────────
    def test_create_order_past_date(self):
        """
        Дата доставки в прошлом (2020-01-01) → 400 или 422.
        """
        url = get_url("/orders/order/")
        body = {**BASE_ORDER_BODY, "delivery_date": "2020-01-01"}
        response = requests.post(url, json=body, headers=get_auth_headers())

        assert response.status_code != 500, \
            f"Сервер упал на прошедшей дате. Ответ: {response.text[:300]}"
        assert response.status_code in [400, 422], \
            f"Заказ с датой в прошлом принят! Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 08.16 ─────────────────────────────────────────────────────────────
    def test_create_order_invalid_payment_type(self):
        """
        Невалидный тип оплаты → 400 или 422.
        """
        url = get_url("/orders/order/")
        body = {**BASE_ORDER_BODY, "payment_type": "bitcoin"}
        response = requests.post(url, json=body, headers=get_auth_headers())

        assert response.status_code != 500, \
            f"Сервер упал на невалидном типе оплаты. Ответ: {response.text[:300]}"
        assert response.status_code in [400, 422], \
            f"Заказ с невалидным payment_type принят! Статус: {response.status_code}"

    # ── 08.19 ─────────────────────────────────────────────────────────────
    def test_get_nonexistent_order(self):
        """
        Несуществующий заказ → 404.
        """
        url = get_url("/orders/order/999999/")
        response = requests.get(url, headers=get_auth_headers())

        assert response.status_code != 500, \
            f"Сервер упал. Ответ: {response.text[:300]}"
        assert response.status_code == 404, \
            f"Ожидали 404. Статус: {response.status_code}"

    # ── 08.25 ─────────────────────────────────────────────────────────────
    def test_idor_get_other_user_order(self):
        """
        IDOR: чужой заказ → 404.
        """
        url = get_url("/orders/order/99999/")
        response = requests.get(url, headers=get_auth_headers())

        assert response.status_code == 404, \
            f"IDOR! Чужой заказ доступен. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 08.20 ─────────────────────────────────────────────────────────────
    def test_orders_by_date_invalid_format(self):
        """
        Невалидный формат даты DD-MM-YYYY → 400 или 404.
        """
        url = get_url("/orders/order/by-date/13-05-2026/")
        response = requests.get(url, headers=get_auth_headers())

        assert response.status_code != 500, \
            f"Сервер упал на невалидном формате даты. Ответ: {response.text[:300]}"
        assert response.status_code in [400, 404], \
            f"Невалидный формат даты принят! Статус: {response.status_code}"

    # ── 08.21 ─────────────────────────────────────────────────────────────
    def test_invalid_order_action(self):
        """
        Невалидный action → 400, 404 или 422.
        """
        url = get_url("/orders/order/999999/action/")
        response = requests.post(
            url,
            json={"action": "fly_to_moon"},
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал на невалидном action. Ответ: {response.text[:300]}"
        assert response.status_code in [400, 404, 422], \
            f"Невалидный action принят! Статус: {response.status_code}"

    # ── 08.14 ─────────────────────────────────────────────────────────────
    def test_merge_orders_no_guest_token(self):
        """
        Merge без guest_token → 400.
        """
        url = get_url("/orders/order/merge/")
        response = requests.post(
            url,
            json={"guest_token": ""},
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал. Ответ: {response.text[:300]}"
        assert response.status_code in [200, 400], \
            f"Неожиданный статус: {response.status_code}"

    # ── 08.26 ─────────────────────────────────────────────────────────────
    def test_xss_in_order_notes(self):
        """
        XSS в поле notes — скрипт не должен вернуться в ответе.
        """
        url = get_url("/orders/order/")
        body = {**BASE_ORDER_BODY, "notes": "<script>alert('xss')</script>"}
        response = requests.post(url, json=body, headers=get_auth_headers())

        assert response.status_code != 500, \
            f"Сервер упал на XSS. Ответ: {response.text[:300]}"
        assert "<script>alert" not in response.text, \
            f"XSS не санитизирован — скрипт вернулся в ответе!"

    # ── 08.7 ──────────────────────────────────────────────────────────────
    def test_orders_by_valid_date_format(self):
        """
        Заказы по дате YYYY-MM-DD — не 500. Пустой результат ок.
        """
        url = get_url(f"/orders/order/by-date/{_DELIVERY_DATE}/")
        response = requests.get(url, params={"page": 1}, headers=get_auth_headers())

        assert response.status_code != 500, \
            f"Сервер упал. Ответ: {response.text[:300]}"
        assert response.status_code in [200, 404], \
            f"Неожиданный статус: {response.status_code}"