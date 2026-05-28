import requests
import pytest
from config import get_url, get_auth_headers


class TestActions:
    """
    Тесты регистрации чека — папка 12 из Postman-коллекции.
    """

    # ── 12.1 ──────────────────────────────────────────────────────────────
    def test_promotions_list(self):
        """
        Список акций для регистрации чека — пустой список ок.
        """
        url = get_url("/actions/registration/")
        response = requests.get(url, headers=get_auth_headers())

        assert response.status_code == 200, \
            f"Список акций недоступен. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 12.2 ──────────────────────────────────────────────────────────────
    def test_user_actions(self):
        """
        Акции пользователя — история регистраций чеков.
        """
        url = get_url("/actions/user/")
        response = requests.get(url, headers=get_auth_headers())

        assert response.status_code != 500, \
            f"Сервер упал. Ответ: {response.text[:300]}"
        assert response.status_code in [200, 404], \
            f"Акции пользователя недоступны. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 12.8 ──────────────────────────────────────────────────────────────
    def test_user_actions_no_auth(self):
        """
        Акции пользователя без авторизации → 401.
        """
        url = get_url("/actions/user/")
        response = requests.get(
            url,
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 401, \
            f"Акции доступны без токена! Статус: {response.status_code}"

    # ── 12.5 ──────────────────────────────────────────────────────────────
    def test_register_receipt_empty_body(self):
        """
        Регистрация чека с пустым телом → 400.
        """
        url = get_url("/actions/registration/")
        response = requests.post(
            url,
            json={},
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал на пустом теле. Ответ: {response.text[:300]}"
        assert response.status_code == 400, \
            f"Пустое тело принято! Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 12.6 ──────────────────────────────────────────────────────────────
    def test_register_receipt_no_auth(self):
        """
        Регистрация чека без авторизации → 401.
        """
        url = get_url("/actions/registration/")
        response = requests.post(
            url,
            json={"action_id": "1", "receipt_code": "TEST"},
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 401, \
            f"Регистрация чека без токена прошла! Статус: {response.status_code}"

    # ── 12.3 ──────────────────────────────────────────────────────────────
    def test_register_receipt_invalid_code(self):
        """
        Регистрация с невалидным кодом чека (ABC) → 400.
        Минимальная длина кода должна валидироваться.
        """
        url = get_url("/actions/registration/")
        response = requests.post(
            url,
            json={
                "action_id": "1",
                "receipt_code": "ABC",
                "first_name": "QA",
                "last_name": "Test",
            },
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал на невалидном коде. Ответ: {response.text[:300]}"
        assert response.status_code in [400, 404], \
            f"Невалидный код принят! Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 12.4 ──────────────────────────────────────────────────────────────
    def test_register_receipt_digits_in_name(self):
        """
        Цифры и спецсимволы в имени → 400.
        Имя не должно содержать цифры или символы типа @@@.
        """
        url = get_url("/actions/registration/")
        response = requests.post(
            url,
            json={
                "action_id": "1",
                "receipt_code": "TEST12345",
                "first_name": "12345",
                "last_name": "@@@",
            },
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал на цифрах в имени. Ответ: {response.text[:300]}"
        assert response.status_code in [400, 404], \
            f"Цифры в имени приняты! Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 12.7 ──────────────────────────────────────────────────────────────
    def test_register_receipt_very_long_code(self):
        """
        Очень длинный код чека (150 символов) → не 500.
        """
        url = get_url("/actions/registration/")
        response = requests.post(
            url,
            json={
                "action_id": "1",
                "receipt_code": "X" * 150,
            },
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал на длинном коде. Ответ: {response.text[:300]}"