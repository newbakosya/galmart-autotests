import requests
import pytest
from config import get_url, get_auth_headers, get_full_headers
import os
from dotenv import load_dotenv
load_dotenv()

_DELIVERY_DATE = os.getenv("DELIVERY_DATE", "2026-06-01")
_DELIVERY_TIME = os.getenv("DELIVERY_TIME", "10:00 - 12:00")
_ADDRESS_ID = os.getenv("ADDRESS_ID", "")
_CARD_ID = os.getenv("CARD_ID", "")


class TestSecurity:
    # тесты безопасности и idor — папка 14

    def test_idor_put_other_user_address(self):
        # id 27454 принадлежит другому аккаунту — должен быть 403 или 404
        url = get_url("/account/address/27454/")
        resp = requests.put(
            url,
            json={"name": "QA IDOR Test", "address": "улица Кабанбай батыра 10", "city": 2, "latitude": 51.1801, "longitude": 71.446},
            headers=get_auth_headers(),
        )
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code in [403, 404], f"idor! чужой адрес изменён, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_idor_patch_other_user_address(self):
        url = get_url("/account/address/27454/")
        resp = requests.patch(url, json={"comment": "idor test"}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code in [403, 404], f"idor! чужой адрес изменён через patch, статус: {resp.status_code}"

    def test_idor_delete_other_user_address(self):
        url = get_url("/account/address/27454/")
        resp = requests.delete(url, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code in [403, 404], f"idor! чужой адрес удалён, статус: {resp.status_code}"

    def test_idor_get_other_user_order(self):
        url = get_url("/orders/order/99999/")
        resp = requests.get(url, headers=get_auth_headers())
        assert resp.status_code == 404, f"idor! чужой заказ доступен, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_no_auth_protected_endpoint(self):
        url = get_url("/account/profile/")
        resp = requests.get(url, headers={"Content-Type": "application/json"})
        assert resp.status_code == 401, f"профиль доступен без токена! статус: {resp.status_code}"

    def test_sql_injection_in_search(self):
        url = get_url("/catalog/goods/")
        resp = requests.get(url, params={"search": "' OR '1'='1"}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал на sql инъекции! ответ: {resp.text[:200]}"

    def test_mass_assignment_in_profile(self):
        # пробуем присвоить is_admin=true — сервер должен игнорировать
        url = get_url("/account/profile/")
        resp = requests.patch(url, json={"name": "QA", "lastname": "Test", "is_admin": True, "role": "superuser"}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал на mass assignment, ответ: {resp.text[:200]}"
        assert resp.status_code in [200, 400], f"неожиданный статус: {resp.status_code}"

    def test_expired_token(self):
        # истёкший токен — 401
        url = get_url("/account/profile/")
        resp = requests.get(
            url,
            headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MDAwMDAwMDB9.invalid", "Content-Type": "application/json"},
        )
        assert resp.status_code == 401, f"истёкший токен принят! статус: {resp.status_code}"

    def test_idor_own_favorites_only(self):
        # передаём чужой user_id — апи должен его игнорировать
        url = get_url("/catalog/favorite/")
        resp = requests.get(url, params={"user_id": 99999}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code in [200, 400], f"неожиданный статус: {resp.status_code}"

    def test_xss_in_order_notes(self):
        # xss в notes — скрипт не должен вернуться в ответе
        url = get_url("/orders/order/")
        body = {
            "address": _ADDRESS_ID,
            "delivery_date": _DELIVERY_DATE,
            "delivery_time": _DELIVERY_TIME,
            "card": _CARD_ID,
            "notes": "<script>alert('xss')</script>",
            "bonuses": 0,
            "leave_at_door": False,
            "replace_items_action": "call",
            "allow_unavailable_items": True,
        }
        resp = requests.post(url, json=body, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert "<script>alert" not in resp.text, "xss не санитизирован — скрипт вернулся в ответе!"
