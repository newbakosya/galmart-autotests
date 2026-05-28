import requests
import pytest
from config import get_url, get_auth_headers


class TestChat:
    """
    Тесты чата поддержки — папка 11 из Postman-коллекции.
    """

    # ── 11.1 ──────────────────────────────────────────────────────────────
    @pytest.mark.xfail(reason="BUG: /chat/messages/support/ возвращает 404 на stage", strict=True)
    def test_chat_history(self):
        """
        История чата с поддержкой — пустой список ок.
        """
        url = get_url("/chat/messages/support/")
        response = requests.get(url, headers=get_auth_headers())

        assert response.status_code == 200, \
            f"История чата недоступна. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 11.2 ──────────────────────────────────────────────────────────────
    @pytest.mark.xfail(reason="BUG: /chat/messages/support/ возвращает 404 на stage", strict=True)
    def test_chat_history_pagination(self):
        """
        История чата с пагинацией page=1.
        """
        url = get_url("/chat/messages/support/")
        response = requests.get(
            url,
            params={"page": 1},
            headers=get_auth_headers(),
        )
        assert response.status_code == 200, \
            f"Чат с пагинацией недоступен. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 11.4 ──────────────────────────────────────────────────────────────
    @pytest.mark.xfail(reason="BUG: /chat/messages/support/ возвращает 404 — 401 не проверить", strict=True)
    def test_chat_history_no_auth(self):
        """
        История чата без авторизации → 401.
        """
        url = get_url("/chat/messages/support/")
        response = requests.get(
            url,
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 401, \
            f"Чат доступен без токена! Статус: {response.status_code}"

    # ── 11.5 ──────────────────────────────────────────────────────────────
    def test_chat_invalid_key(self):
        """
        Чат с невалидным ключом → не 500.
        """
        url = get_url("/chat/messages/invalid_key_xyz/")
        response = requests.get(url, headers=get_auth_headers())

        assert response.status_code != 500, \
            f"Сервер упал на невалидном ключе. Ответ: {response.text[:300]}"
        assert response.status_code in [400, 404], \
            f"Невалидный ключ принят! Статус: {response.status_code}"

    # ── 11.3 ──────────────────────────────────────────────────────────────
    @pytest.mark.xfail(reason="BUG: upload_image ожидает multipart/form-data, а не base64 JSON", strict=True)
    def test_upload_image_to_chat(self):
        """
        Загрузка изображения в чат — минимальный 1x1 PNG base64.
        """
        url = get_url("/addits/upload_image/")
        tiny_png = (
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ"
            "AAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
        response = requests.post(
            url,
            json={"image": tiny_png},
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал при загрузке изображения. Ответ: {response.text[:300]}"
        assert response.status_code in [200, 201], \
            f"Изображение не загружено. Статус: {response.status_code}. Ответ: {response.text[:300]}"