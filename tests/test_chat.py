import requests
import pytest
from config import get_url, get_auth_headers


class TestChat:
    # тесты чата поддержки — папка 11

    @pytest.mark.xfail(reason="BUG: /chat/messages/support/ возвращает 404 на stage", strict=True)
    def test_chat_history(self):
        url = get_url("/chat/messages/support/")
        resp = requests.get(url, headers=get_auth_headers())
        assert resp.status_code == 200, f"история чата недоступна, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    @pytest.mark.xfail(reason="BUG: /chat/messages/support/ возвращает 404 на stage", strict=True)
    def test_chat_history_pagination(self):
        url = get_url("/chat/messages/support/")
        resp = requests.get(url, params={"page": 1}, headers=get_auth_headers())
        assert resp.status_code == 200, f"чат с пагинацией недоступен, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    @pytest.mark.xfail(reason="BUG: /chat/messages/support/ возвращает 404 — 401 не проверить", strict=True)
    def test_chat_history_no_auth(self):
        # эндпоинт возвращает 404 на stage, поэтому 401 не проверить
        url = get_url("/chat/messages/support/")
        resp = requests.get(url, headers={"Content-Type": "application/json"})
        assert resp.status_code == 401, f"чат доступен без токена! статус: {resp.status_code}"

    def test_chat_invalid_key(self):
        # невалидный ключ чата — не 500
        url = get_url("/chat/messages/invalid_key_xyz/")
        resp = requests.get(url, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал на невалидном ключе, ответ: {resp.text[:200]}"
        assert resp.status_code in [400, 404], f"невалидный ключ принят! статус: {resp.status_code}"

    @pytest.mark.xfail(reason="BUG: upload_image ожидает multipart/form-data, а не base64 JSON", strict=True)
    def test_upload_image_to_chat(self):
        # апи ожидает multipart, а не json с base64 — расхождение с документацией
        url = get_url("/addits/upload_image/")
        tiny_png = (
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ"
            "AAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
        resp = requests.post(url, json={"image": tiny_png}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code in [200, 201], f"изображение не загружено, статус: {resp.status_code}"
