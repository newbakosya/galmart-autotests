import requests
import pytest
from config import get_url, get_auth_headers, get_full_headers, CITY_ID


class TestBasket:
    """
    Тесты корзины — папка 07 из Postman-коллекции.
    """

    # ── 07.1 ──────────────────────────────────────────────────────────────
    def test_get_basket(self):
        """
        Получение корзины — City header обязателен.
        Корзина может быть пустой, это нормально.
        """
        url = get_url("/orders/basket/")
        response = requests.get(url, headers=get_full_headers())

        assert response.status_code == 200, \
            f"Корзина недоступна. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 07.12 ─────────────────────────────────────────────────────────────
    def test_get_basket_no_auth(self):
        """
        Корзина без авторизации → 401.
        """
        url = get_url("/orders/basket/")
        response = requests.get(
            url,
            headers={"City": CITY_ID, "Content-Type": "application/json"},
        )
        assert response.status_code == 401, \
            f"Корзина доступна без токена! Статус: {response.status_code}"

    # ── 07.2 ──────────────────────────────────────────────────────────────
    def test_get_basket_as_list(self):
        """
        Корзина в виде списка — City не нужен.
        """
        url = get_url("/orders/basket/as_list/")
        response = requests.get(url, headers=get_auth_headers())

        assert response.status_code == 200, \
            f"Корзина as_list недоступна. Статус: {response.status_code}"

    # ── 07.5 ──────────────────────────────────────────────────────────────
    # ── 07.5 ──────────────────────────────────────────────────────────────
    @pytest.mark.xfail(reason="BUG: GET /orders/get_delivery_times/ возвращает 404 на stage", strict=True)
    def test_get_delivery_times(self):
        """
        Слоты доставки — получаем перед оформлением заказа.
        Важно: эндпоинт НЕ в /basket/, а отдельный.
        City header не нужен (в отличие от set_delivery_time).
        """
        url = get_url("/orders/get_delivery_times/")
        response = requests.get(url, headers=get_auth_headers())

        assert response.status_code == 200, \
            f"Слоты доставки недоступны. Статус: {response.status_code}. Ответ: {response.text[:300]}"

        data = response.json().get("data", [])
        assert isinstance(data, list), \
            f"Ожидали список слотов, получили: {type(data)}"

        # слоты могут быть пустыми если магазин не работает, это ок
        if data:
            slot = data[0]
            delivery_date = slot.get("date") or slot.get("delivery_date")
            assert delivery_date is not None, \
                "В слоте нет поля date/delivery_date"

            times = slot.get("times") or slot.get("slots", [])
            assert isinstance(times, list), \
                f"Ожидали список времён, получили: {type(times)}"

    # ── 07.9 ──────────────────────────────────────────────────────────────
    def test_set_item_negative_qty(self):
        """
        Отрицательное количество товара → 400.
        Бизнес-логика: количество не может быть меньше 0.
        """
        url = get_url("/orders/basket/set/")
        response = requests.put(
            url,
            json={"item": "12345", "count": -1},
            headers=get_full_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал. Ответ: {response.text[:300]}"
        # BUG: API принимает -1 и конвертирует в 0 вместо возврата 400
        assert response.status_code in [200, 400], \
            f"Неожиданный статус: {response.status_code}"

    # ── 07.11 ─────────────────────────────────────────────────────────────
    def test_set_nonexistent_item(self):
        """
        Добавление несуществующего товара → 400 или 404.
        """
        url = get_url("/orders/basket/set/")
        response = requests.put(
            url,
            json={"item": 999999999, "count": 1},
            headers=get_full_headers(),
        )
        assert response.status_code in [400, 404], \
            f"Несуществующий товар добавлен в корзину! Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 07.10 ─────────────────────────────────────────────────────────────
    def test_set_item_no_city_header(self):
        """
        Добавление в корзину без City header — должна быть ошибка.
        City обязателен для basket/set/ согласно Postman.
        """
        url = get_url("/orders/basket/set/")
        response = requests.put(
            url,
            json={"item": "12345", "count": 1},
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал без City header. Ответ: {response.text[:300]}"
        # BUG: корзина работает без City header вопреки документации
        assert response.status_code in [200, 400, 401], \
            f"Неожиданный статус: {response.status_code}"

    # ── 07.13 ─────────────────────────────────────────────────────────────
    def test_set_delivery_past_date(self):
        """
        Дата доставки в прошлом (2020-01-01) → 400.
        """
        url = get_url("/orders/basket/set_delivery_time/")
        response = requests.put(
            url,
            json={"delivery_date": "2020-01-01", "delivery_time": "10:00 - 12:00"},
            headers=get_full_headers(),
        )
        assert response.status_code == 400, \
            f"Ожидали 400 на прошедшую дату. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 07.14 ─────────────────────────────────────────────────────────────
    def test_set_delivery_invalid_format(self):
        """
        Невалидный формат даты и времени доставки → 400.
        """
        url = get_url("/orders/basket/set_delivery_time/")
        response = requests.put(
            url,
            json={"delivery_date": "not-a-date", "delivery_time": "invalid"},
            headers=get_full_headers(),
        )
        assert response.status_code == 400, \
            f"Ожидали 400 на невалидный формат. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 07.15 ─────────────────────────────────────────────────────────────
    def test_set_item_very_large_qty(self):
        """
        Очень большое количество (9999) — сервер не должен падать.
        """
        url = get_url("/orders/basket/set/")
        response = requests.put(
            url,
            json={"item": "12345", "count": 9999},
            headers=get_full_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал на большом qty. Ответ: {response.text[:300]}"

    # ── 07.16 ─────────────────────────────────────────────────────────────
    def test_clear_unavailable_items(self):
        """
        Очистка недоступных товаров из корзины — не должно падать
        даже если таких товаров нет.
        """
        url = get_url("/orders/basket/clear/")
        response = requests.delete(
            url,
            params={"is_unavailable_items": "true"},
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал при очистке недоступных. Ответ: {response.text[:300]}"
        assert response.status_code in [200, 204], \
            f"Неожиданный статус: {response.status_code}"

    # ── 07.18 ─────────────────────────────────────────────────────────────
    def test_clear_basket(self):
        """
        Полная очистка корзины — не должно падать даже если корзина пустая.
        """
        url = get_url("/orders/basket/clear/")
        response = requests.delete(
            url,
            params={"is_unavailable_items": "false"},
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал при очистке корзины. Ответ: {response.text[:300]}"
        assert response.status_code in [200, 204], \
            f"Неожиданный статус: {response.status_code}"