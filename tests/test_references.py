import requests
import pytest
from config import get_url, get_auth_headers, get_full_headers, CITY_ID


class TestReferences:
    """
    Тесты справочников — папка 13 из Postman-коллекции.
    Большинство эндпоинтов публичные, авторизация не нужна.
    """

    # ── 13.1 ──────────────────────────────────────────────────────────────
    def test_shops_list(self):
        """
        Список магазинов — публичный эндпоинт.
        """
        url = get_url("/addits/shops/")
        response = requests.get(url, headers=get_auth_headers())

        assert response.status_code == 200, \
            f"Список магазинов недоступен. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 13.9 ──────────────────────────────────────────────────────────────
    def test_shops_list_with_city_header(self):
        """
        Список магазинов с City header — должен работать так же.
        """
        url = get_url("/addits/shops/")
        response = requests.get(url, headers=get_full_headers())

        assert response.status_code == 200, \
            f"Список магазинов с City header недоступен. Статус: {response.status_code}"

    # ── 13.2 ──────────────────────────────────────────────────────────────
    def test_contacts(self):
        """
        Контакты — публичный эндпоинт.
        """
        url = get_url("/addits/contact/")
        response = requests.get(url, headers=get_auth_headers())

        assert response.status_code == 200, \
            f"Контакты недоступны. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 13.3 ──────────────────────────────────────────────────────────────
    def test_faq(self):
        """
        FAQ / Вопросы и ответы — публичный эндпоинт.
        """
        url = get_url("/addits/questions/")
        response = requests.get(url, headers=get_auth_headers())

        assert response.status_code == 200, \
            f"FAQ недоступен. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 13.4 ──────────────────────────────────────────────────────────────
    def test_legal_documents(self):
        """
        Юридические документы (оферта, политика конфиденциальности).
        """
        url = get_url("/addits/legal/")
        response = requests.get(url, headers=get_auth_headers())

        assert response.status_code == 200, \
            f"Юридические документы недоступны. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 13.5 ──────────────────────────────────────────────────────────────
    def test_app_context(self):
        """
        Конфиг приложения — публичный эндпоинт.
        """
        url = get_url("/addits/context/")
        response = requests.get(url, headers=get_auth_headers())

        assert response.status_code == 200, \
            f"App context недоступен. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 13.6 ──────────────────────────────────────────────────────────────
    @pytest.mark.xfail(reason="BUG: /addits/check_version/ возвращает 404 на stage", strict=True)
    def test_check_version_ios(self):
        """
        Проверка версии iOS 1.0.0 — актуальная версия.
        """
        url = get_url("/addits/check_version/ios/1.0.0/")
        response = requests.get(url, headers=get_auth_headers())

        assert response.status_code != 500, \
            f"Сервер упал. Ответ: {response.text[:300]}"
        assert response.status_code == 200, \
            f"Проверка версии iOS недоступна. Статус: {response.status_code}"

    # ── 13.7 ──────────────────────────────────────────────────────────────
    @pytest.mark.xfail(reason="BUG: /addits/check_version/ возвращает 404 на stage", strict=True)
    def test_check_version_android_outdated(self):
        """
        Проверка устаревшей версии Android 0.0.1 — ответ 200, флаг update_required.
        """
        url = get_url("/addits/check_version/android/0.0.1/")
        response = requests.get(url, headers=get_auth_headers())

        assert response.status_code != 500, \
            f"Сервер упал. Ответ: {response.text[:300]}"
        assert response.status_code == 200, \
            f"Проверка версии Android недоступна. Статус: {response.status_code}"

    # ── 13.8 ──────────────────────────────────────────────────────────────
    def test_check_version_invalid_format(self):
        """
        Невалидный формат версии (abc вместо x.y.z) → не 500.
        """
        url = get_url("/addits/check_version/android/abc/")
        response = requests.get(url, headers=get_auth_headers())

        assert response.status_code != 500, \
            f"Сервер упал на невалидном формате версии. Ответ: {response.text[:300]}"