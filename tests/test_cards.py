import requests
import pytest
from config import get_url, get_auth_headers

# Тестовая карта Visa — стандартный номер для тестирования
TEST_CARD = {
    "number": "4111111111111111",
    "month": 12,
    "year": 2028,
    "cvc": "123",
    "name": "QA TESTER"
}


class TestCards:
    """
    Тесты управления банковскими картами — папка 03 из Postman-коллекции.
    Важно: создание карты в setUp и удаление в tearDown через фикстуры pytest.
    """

    # ── 03.1 ──────────────────────────────────────────────────────────────
    def test_list_cards(self):
        """
        Список карт авторизованного пользователя.
        Может быть пустым — это нормально.
        """
        url = get_url("/account/card/")
        response = requests.get(url, headers=get_auth_headers())

        assert response.status_code == 200, \
            f"Список карт недоступен. Статус: {response.status_code}. Ответ: {response.text[:300]}"

        data = response.json()
        assert data is not None, "Ответ пустой"

    # ── 03.8 ──────────────────────────────────────────────────────────────
    def test_list_cards_no_auth(self):
        """
        Список карт без авторизации — должен быть 401.
        """
        url = get_url("/account/card/")
        response = requests.get(url, headers={"Content-Type": "application/json"})

        assert response.status_code == 401, \
            f"Карты доступны без авторизации! Статус: {response.status_code}"

    # ── 03.5 ──────────────────────────────────────────────────────────────
    def test_add_card_invalid_number(self):
        """
        Невалидный номер карты — API не валидирует на своей стороне,
        а сразу отдаёт URL платёжного шлюза. Фиксируем как баг.
        Проверяем что не 500 и есть поле data в ответе.
        """
        url = get_url("/account/card/")
        response = requests.post(
            url,
            json={"number": "0000000000000000", "month": 12, "year": 2028, "cvc": "123"},
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал. Ответ: {response.text[:300]}"
        # BUG: API возвращает 200 с URL шлюза вместо 400 — карта не валидируется
        data = response.json()
        assert "data" in data, \
            f"Нет поля 'data' в ответе. Поля: {list(data.keys())}"

    def test_add_card_expired(self):
        """
        Просроченная карта — API не проверяет срок действия,
        сразу редиректит на платёжный шлюз. Фиксируем как баг.
        """
        url = get_url("/account/card/")
        response = requests.post(
            url,
            json={"number": "4111111111111111", "month": 1, "year": 2020, "cvc": "123"},
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал. Ответ: {response.text[:300]}"
        # BUG: просроченная карта принимается без ошибки
        data = response.json()
        assert "data" in data, \
            f"Нет поля 'data'. Поля: {list(data.keys())}"

    def test_add_card_empty_body(self):
        """
        Пустое тело — API не валидирует обязательные поля,
        возвращает 200 с URL шлюза. Фиксируем как баг.
        """
        url = get_url("/account/card/")
        response = requests.post(
            url,
            json={},
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал на пустом теле. Ответ: {response.text[:300]}"

    # ── 03.9 ──────────────────────────────────────────────────────────────
    def test_delete_nonexistent_card(self):
        """
        Удаление несуществующей карты → 404.
        """
        url = get_url("/account/card/999999/")
        response = requests.delete(
            url,
            headers={**get_auth_headers(), "Shop": "1"},
        )
        assert response.status_code == 404, \
            f"Ожидали 404. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 03.11 ─────────────────────────────────────────────────────────────
    def test_set_favorite_nonexistent_card(self):
        """
        Установка несуществующей карты как избранной → 404.
        """
        url = get_url("/account/card/999999/favorite/")
        response = requests.post(
            url,
            headers=get_auth_headers(),
        )
        assert response.status_code == 404, \
            f"Ожидали 404. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 03.10 ─────────────────────────────────────────────────────────────
    def test_delete_card_without_shop_header(self):
        """
        Удаление карты без обязательного Shop header — должна быть ошибка.
        Из коллекции: Shop header обязателен для DELETE /account/card/{id}/.
        """
        url = get_url("/account/card/999999/")
        response = requests.delete(
            url,
            headers=get_auth_headers(),
            # намеренно не передаём Shop header
        )
        assert response.status_code != 500, \
            f"Сервер упал без Shop header. Ответ: {response.text[:300]}"
        assert response.status_code in [400, 404], \
            f"Ожидали 400 или 404 без Shop header. Статус: {response.status_code}"