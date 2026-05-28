import requests
import pytest
from config import get_url, get_auth_headers
import os
from dotenv import load_dotenv
load_dotenv()

_DELIVERY_DATE = os.getenv("DELIVERY_DATE", "2026-06-01")
_DELIVERY_TIME = os.getenv("DELIVERY_TIME", "10:00 - 12:00")
_ADDRESS_ID = os.getenv("ADDRESS_ID", "")
_CARD_ID = os.getenv("CARD_ID", "")


class TestBugProbe:
    # верификация известных багов — проверяем что ничего не регрессировало

    def test_bonus_balance_accessible(self):
        # bp-01: баланс бонусов — эндпоинт живой
        url = get_url("/account/points/")
        resp = requests.get(url, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code == 200, f"баланс бонусов недоступен, статус: {resp.status_code}"

    def test_idor_put_other_address(self):
        # bp-04: idor на чужой адрес — не регрессировал
        url = get_url("/account/address/27454/")
        resp = requests.put(
            url,
            json={"name": "BUG-PROBE IDOR", "address": "улица Кабанбай батыра 10", "city": 2, "latitude": 51.1801, "longitude": 71.446},
            headers=get_auth_headers(),
        )
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code in [403, 404], f"idor! чужой адрес изменён, статус: {resp.status_code}"

    def test_refresh_token_bug(self):
        # bp-06: bug-052 был починен — refresh_token больше не падает с 500
        url = get_url("/account/refresh_token/")
        resp = requests.post(url, json={"refresh": "invalid_token_for_probe"}, headers={"Content-Type": "application/json"})
        assert resp.status_code != 500, f"bug-052 регрессировал: refresh_token вернул 500, ответ: {resp.text[:200]}"

    def test_logout(self):
        # bp-07: logout без 500, 400 допустим если токен уже инвалидирован
        url = get_url("/account/logout/")
        resp = requests.post(url, headers=get_auth_headers())
        assert resp.status_code != 500, f"bug-050: logout вернул 500, ответ: {resp.text[:200]}"
        assert resp.status_code in [200, 204, 400], f"неожиданный статус: {resp.status_code}"

    def test_homepage_double_call(self):
        # bp-08: homepage не падает при двойном вызове
        url = get_url("/catalog/homepage/")
        resp1 = requests.get(url, headers=get_auth_headers())
        resp2 = requests.get(url, headers=get_auth_headers())
        assert resp1.status_code != 500, f"первый вызов упал, ответ: {resp1.text[:200]}"
        assert resp2.status_code != 500, f"второй вызов упал, ответ: {resp2.text[:200]}"
        assert resp1.status_code == resp2.status_code, f"разные статусы: {resp1.status_code} vs {resp2.status_code}"

    @pytest.mark.xfail(reason="BUG-044: bonus/transaction/{id} возвращает data=[]", strict=True)
    def test_bonus_transaction_by_id(self):
        # bp-09: транзакция по id возвращает data=[] — баг не починен
        url = get_url("/bonus/transaction/1/")
        resp = requests.get(url, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code in [200, 404], f"неожиданный статус: {resp.status_code}"
        if resp.status_code == 200:
            data = resp.json().get("data")
            assert data != [], "bug-044 не исправлен: data=[] на существующей транзакции"

    def test_price_snapshot_in_order(self):
        # bp-05: проверяем что заказы не падают в 500
        url = get_url("/orders/order/999999/")
        resp = requests.get(url, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code in [200, 404], f"неожиданный статус: {resp.status_code}"
