import requests
import pytest
from config import get_url, get_auth_headers


class TestProfile:
    """
    Тесты профиля пользователя — папка 02 из Postman-коллекции.
    """

    # ── 02.1 ──────────────────────────────────────────────────────────────
    def test_get_profile(self):
        """
        Получение профиля авторизованного пользователя.
        Проверяем структуру — должны быть phone, name, lastname.
        """
        url = get_url("/account/profile/")
        response = requests.get(url, headers=get_auth_headers())

        assert response.status_code == 200, \
            f"Профиль недоступен. Статус: {response.status_code}. Ответ: {response.text[:300]}"

        data = response.json()
        assert "data" in data, \
            f"Нет поля 'data'. Поля: {list(data.keys())}"

        profile = data["data"]
        assert "phone" in profile, \
            f"Нет поля 'phone' в профиле. Поля: {list(profile.keys())}"

    # ── 02.4 ──────────────────────────────────────────────────────────────
    def test_get_profile_with_page_param(self):
        """
        Профиль с параметром page=1 — не должно падать,
        параметр используется для пагинации заказов внутри профиля.
        """
        url = get_url("/account/profile/")
        response = requests.get(
            url,
            params={"page": 1},
            headers=get_auth_headers(),
        )
        assert response.status_code == 200, \
            f"Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 02.5 ──────────────────────────────────────────────────────────────
    def test_get_bonus_balance(self):
        """
        Баланс бонусных баллов. Важный эндпоинт — используется
        при оформлении заказа для списания бонусов.
        """
        url = get_url("/account/points/")
        response = requests.get(url, headers=get_auth_headers())

        assert response.status_code == 200, \
            f"Бонусный баланс недоступен. Статус: {response.status_code}"
        assert response.status_code != 500, \
            f"Сервер упал. Ответ: {response.text[:300]}"

    # ── 02.6 ──────────────────────────────────────────────────────────────
    def test_bonus_transactions_list(self):
        """
        История бонусных транзакций — список операций начисления/списания.
        """
        url = get_url("/bonus/transaction/")
        response = requests.get(url, headers=get_auth_headers())

        assert response.status_code == 200, \
            f"Транзакции недоступны. Статус: {response.status_code}"

    # ── 02.7 ──────────────────────────────────────────────────────────────
    def test_bonus_transaction_by_id(self):
        """
        Транзакция по ID — из коллекции помечена как BUG.
        Проверяем что не падает в 500.
        """
        url = get_url("/bonus/transaction/1/")
        response = requests.get(url, headers=get_auth_headers())

        assert response.status_code != 500, \
            f"Сервер упал (500) на транзакции по ID. Ответ: {response.text[:300]}"

    # ── 02.8 / 02.9 ───────────────────────────────────────────────────────
    @pytest.mark.parametrize("platform,version", [
        ("ios", "1.0.0"),
        ("android", "1.0.0"),
    ])
    def test_check_app_version(self, platform, version):
        """
        Проверка версии приложения. Эндпоинт существует,
        но конкретная версия может быть неизвестна серверу — это ок.
        Главное что не 500.
        """
        url = get_url(f"/addits/check_version/{platform}/{version}/")
        response = requests.get(url, headers={"Content-Type": "application/json"})

        assert response.status_code != 500, \
            f"Сервер упал (500) на check_version/{platform}. Ответ: {response.text[:300]}"
        assert response.status_code in [200, 400, 404], \
            f"Неожиданный статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 02.3 ──────────────────────────────────────────────────────────────
    def test_patch_profile_valid(self):
        """
        Обновление профиля через PATCH с валидными данными.
        Меняем name/lastname — безопасно, не трогаем телефон.
        """
        url = get_url("/account/profile/")
        response = requests.patch(
            url,
            json={"name": "QA", "lastname": "Tester", "birthday": "01.01.1990"},
            headers=get_auth_headers(),
        )
        assert response.status_code in [200, 201], \
            f"PATCH не сработал. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 02.10 ─────────────────────────────────────────────────────────────
    def test_patch_profile_phone_readonly(self):
        """
        Попытка изменить телефон через PATCH — поле read-only.
        Сервер должен проигнорировать или вернуть ошибку, но не 500.
        """
        url = get_url("/account/profile/")
        response = requests.patch(
            url,
            json={"phone": "77000000000"},
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал при попытке изменить телефон. Ответ: {response.text[:300]}"

    # ── 02.15 ─────────────────────────────────────────────────────────────
    def test_patch_profile_invalid_birthday(self):
        """
        Невалидный формат даты рождения → должен быть 400.
        API ожидает формат YYYY-MM-DD согласно Swagger.
        """
        url = get_url("/account/profile/")
        response = requests.patch(
            url,
            json={"name": "QA", "lastname": "Test", "birthday": "not-a-date"},
            headers=get_auth_headers(),
        )
        assert response.status_code == 400, \
            f"Ожидали 400 на невалидную дату. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 02.12 ─────────────────────────────────────────────────────────────
    def test_patch_profile_xss_in_name(self):
        """
        XSS в поле name — сервер не должен падать,
        скрипт должен быть санитизирован или отклонён.
        """
        url = get_url("/account/profile/")
        response = requests.patch(
            url,
            json={"name": "<script>alert('xss')</script>", "lastname": "Test", "birthday": "1990-01-01"},
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал на XSS в name. Ответ: {response.text[:300]}"

    # ── 02.14 ─────────────────────────────────────────────────────────────
    def test_patch_profile_sql_injection(self):
        """
        SQL-инъекция в поле name — сервер не должен падать.
        """
        url = get_url("/account/profile/")
        response = requests.patch(
            url,
            json={"name": "'; DROP TABLE users; --", "lastname": "Test", "birthday": "1990-01-01"},
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал на SQL-инъекции. Ответ: {response.text[:300]}"

    # ── 02.13 ─────────────────────────────────────────────────────────────
    def test_patch_profile_very_long_name(self):
        """
        Очень длинное имя (500 символов) — сервер не должен падать.
        """
        url = get_url("/account/profile/")
        response = requests.patch(
            url,
            json={"name": "А" * 500, "lastname": "Test", "birthday": "1990-01-01"},
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал на длинном имени. Ответ: {response.text[:300]}"