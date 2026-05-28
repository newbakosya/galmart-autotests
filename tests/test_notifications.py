import requests
import pytest
from config import get_url, get_auth_headers


class TestNotifications:
    # тесты уведомлений — папка 10

    def test_notifications_tab_orders(self):
        url = get_url("/notifications/")
        resp = requests.get(url, params={"tab": "orders", "page": 1, "limit": 10}, headers=get_auth_headers())
        assert resp.status_code == 200, f"уведомления orders недоступны, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_notifications_tab_bonuses(self):
        url = get_url("/notifications/")
        resp = requests.get(url, params={"tab": "bonuses", "page": 1, "limit": 10}, headers=get_auth_headers())
        assert resp.status_code == 200, f"уведомления bonuses недоступны, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    @pytest.mark.xfail(reason="BUG: tab=news возвращает ошибку на stage", strict=False)
    def test_notifications_tab_news(self):
        # на stage был баг с этим табом, xfail на случай регрессии
        url = get_url("/notifications/")
        resp = requests.get(url, params={"tab": "news", "page": 1, "limit": 10}, headers=get_auth_headers())
        assert resp.status_code == 200, f"уведомления news недоступны, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_notification_counters(self):
        # счётчики должны быть доступны всегда
        url = get_url("/notifications/counters/")
        resp = requests.get(url, headers=get_auth_headers())
        assert resp.status_code == 200, f"счётчики недоступны, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_notification_counters_no_auth(self):
        url = get_url("/notifications/counters/")
        resp = requests.get(url, headers={"Content-Type": "application/json"})
        assert resp.status_code == 401, f"счётчики доступны без токена! статус: {resp.status_code}"

    @pytest.mark.xfail(reason="BUG: push_token не принимает тестовый токен, возвращает 400", strict=True)
    def test_push_token_register(self):
        # апи не принимает тестовые токены — баг
        url = get_url("/notifications/push_token/")
        resp = requests.post(url, json={"token": "test_device_token_qa_12345", "device_type": "android"}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code in [200, 201], f"push-токен не зарегистрирован, статус: {resp.status_code}"

    def test_push_token_empty_body(self):
        url = get_url("/notifications/push_token/")
        resp = requests.post(url, json={}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code == 400, f"пустой push-токен принят! статус: {resp.status_code}"

    def test_push_token_invalid_device_type(self):
        url = get_url("/notifications/push_token/")
        resp = requests.post(url, json={"token": "test", "device_type": "windows_phone"}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал на невалидном device_type, ответ: {resp.text[:200]}"

    def test_notifications_invalid_tab(self):
        url = get_url("/notifications/")
        resp = requests.get(url, params={"tab": "invalid_xyz"}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал на невалидном tab, ответ: {resp.text[:200]}"

    def test_notifications_no_tab_param(self):
        url = get_url("/notifications/")
        resp = requests.get(url, params={"page": 1}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал без параметра tab, ответ: {resp.text[:200]}"

    def test_notifications_page_out_of_range(self):
        url = get_url("/notifications/")
        resp = requests.get(url, params={"tab": "orders", "page": 9999, "limit": 10}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал на странице 9999, ответ: {resp.text[:200]}"

    def test_notifications_page_2(self):
        url = get_url("/notifications/")
        resp = requests.get(url, params={"tab": "orders", "page": 2, "limit": 10}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал на странице 2, ответ: {resp.text[:200]}"
        assert resp.status_code == 200, f"страница 2 недоступна, статус: {resp.status_code}"
