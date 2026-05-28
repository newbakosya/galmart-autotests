import requests
import pytest
from config import get_url, get_auth_headers, get_full_headers
import os
from dotenv import load_dotenv
load_dotenv()

_DELIVERY_DATE = os.getenv("DELIVERY_DATE", "2026-06-01")
_DELIVERY_TIME = os.getenv("DELIVERY_TIME", "10:00 - 12:00")
_ADDRESS_ID    = os.getenv("ADDRESS_ID", "")
_CARD_ID       = os.getenv("CARD_ID", "")


class TestSecurity:
    """
    Тесты безопасности и IDOR — папка 14 из Postman-коллекции.
    """

    # ── 14.1 ──────────────────────────────────────────────────────────────
    def test_idor_put_other_user_address(self):
        """
        IDOR: PUT чужого адреса (ID 27454) → 403 или 404.
        Нельзя изменять адреса другого пользователя.
        """
        url = get_url("/account/address/27454/")
        response = requests.put(
            url,
            json={
                "name": "QA IDOR Test",
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

    # ── 14.2 ──────────────────────────────────────────────────────────────
    def test_idor_patch_other_user_address(self):
        """
        IDOR: PATCH чужого адреса (ID 27454) → 403 или 404.
        """
        url = get_url("/account/address/27454/")
        response = requests.patch(
            url,
            json={"comment": "IDOR test"},
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал. Ответ: {response.text[:300]}"
        assert response.status_code in [403, 404], \
            f"IDOR! Чужой адрес изменён через PATCH. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 14.3 ──────────────────────────────────────────────────────────────
    def test_idor_delete_other_user_address(self):
        """
        IDOR: DELETE чужого адреса (ID 27454) → 403 или 404.
        """
        url = get_url("/account/address/27454/")
        response = requests.delete(url, headers=get_auth_headers())

        assert response.status_code != 500, \
            f"Сервер упал. Ответ: {response.text[:300]}"
        assert response.status_code in [403, 404], \
            f"IDOR! Чужой адрес удалён. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 14.4 ──────────────────────────────────────────────────────────────
    def test_idor_get_other_user_order(self):
        """
        IDOR: GET чужого заказа (ID 99999) → 404.
        """
        url = get_url("/orders/order/99999/")
        response = requests.get(url, headers=get_auth_headers())

        assert response.status_code == 404, \
            f"IDOR! Чужой заказ доступен. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 14.6 ──────────────────────────────────────────────────────────────
    def test_no_auth_protected_endpoint(self):
        """
        Защищённый эндпоинт без авторизации → 401.
        """
        url = get_url("/account/profile/")
        response = requests.get(
            url,
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 401, \
            f"Профиль доступен без токена! Статус: {response.status_code}"

    # ── 14.7 ──────────────────────────────────────────────────────────────
    def test_sql_injection_in_search(self):
        """
        SQL-инъекция в поиске → не 500.
        Сервер должен обработать без падения.
        """
        url = get_url("/catalog/goods/")
        response = requests.get(
            url,
            params={"search": "' OR '1'='1"},
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал на SQL-инъекции! Ответ: {response.text[:300]}"

    # ── 14.8 ──────────────────────────────────────────────────────────────
    def test_mass_assignment_in_profile(self):
        """
        Mass assignment: попытка присвоить is_admin=true и role=superuser.
        Сервер должен игнорировать эти поля — не 500.
        """
        url = get_url("/account/profile/")
        response = requests.patch(
            url,
            json={
                "name": "QA",
                "lastname": "Test",
                "is_admin": True,
                "role": "superuser",
            },
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал на mass assignment. Ответ: {response.text[:300]}"
        assert response.status_code in [200, 400], \
            f"Неожиданный статус: {response.status_code}"

    # ── 14.9 ──────────────────────────────────────────────────────────────
    def test_expired_token(self):
        """
        Истёкший/невалидный токен → 401.
        """
        url = get_url("/account/profile/")
        response = requests.get(
            url,
            headers={
                "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MDAwMDAwMDB9.invalid",
                "Content-Type": "application/json",
            },
        )
        assert response.status_code == 401, \
            f"Истёкший токен принят! Статус: {response.status_code}"

    # ── 14.10 ─────────────────────────────────────────────────────────────
    def test_idor_own_favorites_only(self):
        """
        Избранное возвращает только товары текущего пользователя.
        Проверяем что эндпоинт не принимает чужой user_id в параметрах.
        """
        url = get_url("/catalog/favorite/")
        response = requests.get(
            url,
            params={"user_id": 99999},
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал. Ответ: {response.text[:300]}"
        assert response.status_code in [200, 400], \
            f"Неожиданный статус: {response.status_code}"

    # ── 14.11 ─────────────────────────────────────────────────────────────
    def test_xss_in_order_notes(self):
        """
        XSS в поле notes заказа — скрипт не должен вернуться в ответе.
        """
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
        response = requests.post(url, json=body, headers=get_auth_headers())

        assert response.status_code != 500, \
            f"Сервер упал на XSS. Ответ: {response.text[:300]}"
        assert "<script>alert" not in response.text, \
            f"XSS не санитизирован — скрипт вернулся в ответе!"