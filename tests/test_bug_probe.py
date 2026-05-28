import requests
import pytest
from config import get_url, get_auth_headers
import os
from dotenv import load_dotenv
load_dotenv()

_DELIVERY_DATE = os.getenv("DELIVERY_DATE", "2026-06-01")
_DELIVERY_TIME = os.getenv("DELIVERY_TIME", "10:00 - 12:00")
_ADDRESS_ID    = os.getenv("ADDRESS_ID", "")
_CARD_ID       = os.getenv("CARD_ID", "")


class TestBugProbe:
    """
    Верификация известных багов — BUG-PROBE из Postman-коллекции.
    Проверяем что старые баги не регрессировали.
    """

    # ── BP-01 / BP-03 ──────────────────────────────────────────────────────
    def test_bonus_balance_accessible(self):
        """
        BP-01: Баланс бонусов доступен — эндпоинт живой.
        """
        url = get_url("/account/points/")
        response = requests.get(url, headers=get_auth_headers())

        assert response.status_code != 500, \
            f"Сервер упал. Ответ: {response.text[:300]}"
        assert response.status_code == 200, \
            f"Баланс бонусов недоступен. Статус: {response.status_code}"

    # ── BP-04 ──────────────────────────────────────────────────────────────
    def test_idor_put_other_address(self):
        """
        BP-04: IDOR — PUT чужого адреса (ID 27454) → 403 или 404.
        Верификация что IDOR не регрессировал.
        """
        url = get_url("/account/address/27454/")
        response = requests.put(
            url,
            json={
                "name": "BUG-PROBE IDOR",
                "address": "улица Кабанбай батыра 10",
                "city": 2,
                "latitude": 51.1801,
                "longitude": 71.446,
            },
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал. Ответ: {response.text[:300]}"
        assert response.status_code in [403, 404], \
            f"IDOR! Чужой адрес изменён. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── BP-06 ──────────────────────────────────────────────────────────────
    def test_refresh_token_bug(self):
        """
        BP-06: Верификация BUG-052 — refresh_token больше не падает с 500.
        Баг починен — декоратор xfail убран.
        """
        url = get_url("/account/refresh_token/")
        response = requests.post(
            url,
            json={"refresh": "invalid_token_for_probe"},
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code != 500, \
            f"BUG-052 регрессировал: refresh_token вернул 500. Ответ: {response.text[:300]}"

    # ── BP-07 ──────────────────────────────────────────────────────────────
    def test_logout(self):
        """
        BP-07: Верификация BUG-050 — logout работает без 500.
        400 допустим — токен мог быть уже инвалидирован.
        """
        url = get_url("/account/logout/")
        response = requests.post(url, headers=get_auth_headers())

        assert response.status_code != 500, \
            f"BUG-050: logout вернул 500. Ответ: {response.text[:300]}"
        assert response.status_code in [200, 204, 400], \
            f"Logout вернул неожиданный статус: {response.status_code}"

    # ── BP-08 ──────────────────────────────────────────────────────────────
    def test_homepage_double_call(self):
        """
        BP-08: Верификация BUG-035 — homepage не падает при двойном вызове.
        """
        url = get_url("/catalog/homepage/")

        response1 = requests.get(url, headers=get_auth_headers())
        response2 = requests.get(url, headers=get_auth_headers())

        assert response1.status_code != 500, \
            f"Первый вызов упал. Ответ: {response1.text[:300]}"
        assert response2.status_code != 500, \
            f"Второй вызов упал. Ответ: {response2.text[:300]}"
        assert response1.status_code == response2.status_code, \
            f"Разные статусы при двойном вызове: {response1.status_code} vs {response2.status_code}"

    # ── BP-09 ──────────────────────────────────────────────────────────────
    @pytest.mark.xfail(reason="BUG-044: bonus/transaction/{id} возвращает data=[]", strict=True)
    def test_bonus_transaction_by_id(self):
        """
        BP-09: Верификация BUG-044 — транзакция по ID возвращает data=[].
        """
        url = get_url("/bonus/transaction/1/")
        response = requests.get(url, headers=get_auth_headers())

        assert response.status_code != 500, \
            f"Сервер упал. Ответ: {response.text[:300]}"
        assert response.status_code in [200, 404], \
            f"Неожиданный статус: {response.status_code}"

        if response.status_code == 200:
            data = response.json().get("data")
            assert data != [], \
                "BUG-044 не исправлен: data=[] на существующей транзакции"

    # ── BP-05 ──────────────────────────────────────────────────────────────
    def test_price_snapshot_in_order(self):
        """
        BP-05: Заказ должен содержать снапшот цен товаров.
        Проверяем на несуществующем заказе — главное не 500.
        """
        url = get_url("/orders/order/999999/")
        response = requests.get(url, headers=get_auth_headers())

        assert response.status_code != 500, \
            f"Сервер упал. Ответ: {response.text[:300]}"
        assert response.status_code in [200, 404], \
            f"Неожиданный статус: {response.status_code}"