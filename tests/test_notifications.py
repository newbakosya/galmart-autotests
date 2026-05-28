import requests
import pytest
from config import get_url, get_auth_headers


class TestNotifications:
    """
    Тесты уведомлений — папка 10 из Postman-коллекции.
    """

    # ── 10.1 ──────────────────────────────────────────────────────────────
    def test_notifications_tab_orders(self):
        """
        Уведомления по заказам — пустой список ок.
        """
        url = get_url("/notifications/")
        response = requests.get(
            url,
            params={"tab": "orders", "page": 1, "limit": 10},
            headers=get_auth_headers(),
        )
        assert response.status_code == 200, \
            f"Уведомления orders недоступны. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 10.2 ──────────────────────────────────────────────────────────────
    def test_notifications_tab_bonuses(self):
        """
        Уведомления по бонусам — пустой список ок.
        """
        url = get_url("/notifications/")
        response = requests.get(
            url,
            params={"tab": "bonuses", "page": 1, "limit": 10},
            headers=get_auth_headers(),
        )
        assert response.status_code == 200, \
            f"Уведомления bonuses недоступны. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 10.3 ──────────────────────────────────────────────────────────────
    @pytest.mark.xfail(reason="BUG: tab=news возвращает ошибку на stage", strict=False)
    def test_notifications_tab_news(self):
        """
        Уведомления новости — помечен как xfail, известный баг на stage.
        """
        url = get_url("/notifications/")
        response = requests.get(
            url,
            params={"tab": "news", "page": 1, "limit": 10},
            headers=get_auth_headers(),
        )
        assert response.status_code == 200, \
            f"Уведомления news недоступны. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 10.4 ──────────────────────────────────────────────────────────────
    def test_notification_counters(self):
        """
        Счётчики уведомлений — всегда должны быть доступны.
        """
        url = get_url("/notifications/counters/")
        response = requests.get(url, headers=get_auth_headers())

        assert response.status_code == 200, \
            f"Счётчики недоступны. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 10.7 ──────────────────────────────────────────────────────────────
    def test_notification_counters_no_auth(self):
        """
        Счётчики без авторизации → 401.
        """
        url = get_url("/notifications/counters/")
        response = requests.get(
            url,
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 401, \
            f"Счётчики доступны без токена! Статус: {response.status_code}"

    # ── 10.5 ──────────────────────────────────────────────────────────────
    @pytest.mark.xfail(reason="BUG: push_token не принимает тестовый токен, возвращает 400", strict=True)
    def test_push_token_register(self):
        """
        Регистрация push-токена — android device_type.
        """
        url = get_url("/notifications/push_token/")
        response = requests.post(
            url,
            json={"token": "test_device_token_qa_12345", "device_type": "android"},
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал при регистрации push-токена. Ответ: {response.text[:300]}"
        assert response.status_code in [200, 201], \
            f"Push-токен не зарегистрирован. Статус: {response.status_code}"

    # ── 10.10 ─────────────────────────────────────────────────────────────
    def test_push_token_empty_body(self):
        """
        Push-токен с пустым телом → 400.
        """
        url = get_url("/notifications/push_token/")
        response = requests.post(
            url,
            json={},
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал на пустом теле. Ответ: {response.text[:300]}"
        assert response.status_code == 400, \
            f"Пустой push-токен принят! Статус: {response.status_code}"

    # ── 10.11 ─────────────────────────────────────────────────────────────
    def test_push_token_invalid_device_type(self):
        """
        Push-токен с невалидным device_type (windows_phone) → не 500.
        """
        url = get_url("/notifications/push_token/")
        response = requests.post(
            url,
            json={"token": "test", "device_type": "windows_phone"},
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал на невалидном device_type. Ответ: {response.text[:300]}"

    # ── 10.8 ──────────────────────────────────────────────────────────────
    def test_notifications_invalid_tab(self):
        """
        Невалидный tab → не 500. Сервер должен вернуть ошибку валидации.
        """
        url = get_url("/notifications/")
        response = requests.get(
            url,
            params={"tab": "invalid_xyz"},
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал на невалидном tab. Ответ: {response.text[:300]}"

    # ── 10.9 ──────────────────────────────────────────────────────────────
    def test_notifications_no_tab_param(self):
        """
        Без параметра tab → не 500.
        """
        url = get_url("/notifications/")
        response = requests.get(
            url,
            params={"page": 1},
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал без параметра tab. Ответ: {response.text[:300]}"

    # ── 10.12 ─────────────────────────────────────────────────────────────
    def test_notifications_page_out_of_range(self):
        """
        Страница за пределами (9999) → не 500. Пустой список ок.
        """
        url = get_url("/notifications/")
        response = requests.get(
            url,
            params={"tab": "orders", "page": 9999, "limit": 10},
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал на странице 9999. Ответ: {response.text[:300]}"

    # ── 10.6 ──────────────────────────────────────────────────────────────
    def test_notifications_page_2(self):
        """
        Вторая страница уведомлений — не 500. Может быть пустой.
        """
        url = get_url("/notifications/")
        response = requests.get(
            url,
            params={"tab": "orders", "page": 2, "limit": 10},
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал на странице 2. Ответ: {response.text[:300]}"
        assert response.status_code == 200, \
            f"Страница 2 недоступна. Статус: {response.status_code}"