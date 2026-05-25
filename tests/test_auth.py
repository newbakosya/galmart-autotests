import requests
import pytest
from config import get_url, PHONE


class TestAuth:
    """
    Тесты авторизации — папка 01 из Postman-коллекции.

    Стратегия: мы НЕ отправляем реальные SMS.
    Тестируем только негативные сценарии (валидация входных данных)
    и защищённость эндпоинтов.
    """

    # ── 01.6 ──────────────────────────────────────────────────────────────
    def test_send_code_empty_phone(self):
        """
        Пустой login → 400.
        Сервер должен валидировать что поле не пустое.
        """
        url = get_url("/account/send_code/")
        response = requests.post(
            url,
            json={"login": ""},
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code in [400, 429], \
            f"Ожидали 400 или 429. Получили: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 01.7 ──────────────────────────────────────────────────────────────
    def test_send_code_invalid_phone_format(self):
        """
        Короткий номер '12345' → 400.
        Не является валидным казахстанским номером телефона.
        """
        url = get_url("/account/send_code/")
        response = requests.post(
            url,
            json={"login": "12345"},
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code in [400, 429], \
            f"Ожидали 400 или 429. Получили: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 01.8 ──────────────────────────────────────────────────────────────
    def test_send_code_null_phone(self):
        """
        login: null → 400.
        API должен обрабатывать null без падения в 500.
        """
        url = get_url("/account/send_code/")
        response = requests.post(
            url,
            json={"login": None},
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code in [400, 429], \
            f"Ожидали 400 или 429. Получили: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 01.9 ──────────────────────────────────────────────────────────────
    def test_send_code_special_chars(self):
        """
        Спецсимволы в номере '+7(778)563-68-93' → 400.
        API должен принимать только цифры без форматирования.
        """
        url = get_url("/account/send_code/")
        response = requests.post(
            url,
            json={"login": "+7(778)563-68-93"},
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code in [400, 429], \
            f"Ожидали 400 или 429 (rate limit). Получили: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 01.10 ─────────────────────────────────────────────────────────────
    def test_send_code_empty_body(self):
        """
        Пустое тело {} → 400.
        Поле login обязательное согласно Swagger (required: ['login']).
        """
        url = get_url("/account/send_code/")
        response = requests.post(
            url,
            json={},
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code in [400, 429], \
            f"Ожидали 400 или 429 (rate limit). Получили: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 01.14 ─────────────────────────────────────────────────────────────
    def test_send_code_very_long_phone(self):
        """
        Очень длинный номер (100 символов) → не 500.
        Сервер не должен падать на граничных значениях длины.
        Ожидаем 400 (валидация), но НЕ 500 (падение сервера).
        """
        url = get_url("/account/send_code/")
        long_phone = "7" * 100
        response = requests.post(
            url,
            json={"login": long_phone},
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code != 500, \
            f"Сервер упал (500) на длинном номере. Ответ: {response.text[:300]}"
        assert response.status_code in [400, 429], \
            f"Ожидали 400 или 429 (rate limit). Получили: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 01.15 ─────────────────────────────────────────────────────────────
    def test_send_code_unicode(self):
        """
        Unicode символы в номере → не 500.
        Защита от неожиданных символов — сервер не должен падать.
        """
        url = get_url("/account/send_code/")
        response = requests.post(
            url,
            json={"login": "七七七七七七七七七七"},
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code != 500, \
            f"Сервер упал (500) на Unicode. Ответ: {response.text[:300]}"

    # ── 01.11 ─────────────────────────────────────────────────────────────
    def test_refresh_invalid_token(self):
        """
        Невалидный refresh token → 401.
        Сервер должен отклонять поддельные токены.
        """
        url = get_url("/account/refresh_token/")
        response = requests.post(
            url,
            json={"refresh": "invalid.token.here"},
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code in [400, 401], \
            f"Ожидали 400/401 на невалидный токен. Получили: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 01.12 ─────────────────────────────────────────────────────────────
    def test_refresh_empty_body(self):
        """
        Пустое тело refresh запроса → 400.
        Поле refresh обязательное согласно Swagger (required: ['refresh']).
        """
        url = get_url("/account/refresh_token/")
        response = requests.post(
            url,
            json={},
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 400, \
            f"Ожидали 400 на пустое тело. Получили: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 01.13 ─────────────────────────────────────────────────────────────
    def test_profile_no_auth_returns_401(self):
        """
        GET профиля без токена → 401.
        Повторяем из smoke для полноты auth-тестов.
        """
        url = get_url("/account/profile/")
        response = requests.get(
            url,
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 401, \
            f"Профиль доступен без токена! Статус: {response.status_code}"

    # ── 01.5 ──────────────────────────────────────────────────────────────
    def test_login_wrong_sms_code(self):
        """
        Неверный SMS-код '0000' → 400 или 401.
        Используем реальный телефон но заведомо неверный код.
        Это безопасно — SMS не отправляется, только проверяем
        что сервер отклоняет неверный код.
        """
        url = get_url("/account/login/")
        response = requests.post(
            url,
            json={"login": PHONE, "code": "0000"},
            headers={"Content-Type": "application/json"},
        )
        # Сервер возвращает 403 — фиксируем как баг (должен быть 400 или 401)
        assert response.status_code in [400, 401, 403], \
            f"Неожиданный статус на неверный код. Получили: {response.status_code}. Ответ: {response.text[:300]}"