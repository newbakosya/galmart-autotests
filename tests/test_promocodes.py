import requests
import pytest
from config import get_url, get_auth_headers, CITY_ID

PROMO_CODE = "TESTPROMO"


class TestPromocodes:
    """
    Тесты промокодов — папка 09 из Postman-коллекции.
    """

    # ── 09.2 ──────────────────────────────────────────────────────────────
    def test_list_favorite_promos(self):
        """
        Список избранных промокодов — может быть пустым, главное 200.
        """
        url = get_url("/promocode_my/favorites/")
        response = requests.get(url, headers=get_auth_headers())

        assert response.status_code == 200, \
            f"Список промокодов недоступен. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 09.7 ──────────────────────────────────────────────────────────────
    def test_list_promos_no_auth(self):
        """
        Список промокодов без авторизации → 401.
        """
        url = get_url("/promocode_my/favorites/")
        response = requests.get(
            url,
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 401, \
            f"Промокоды доступны без токена! Статус: {response.status_code}"

    # ── 09.5 ──────────────────────────────────────────────────────────────
    def test_apply_invalid_promo(self):
        """
        Применение несуществующего промокода → 400 или 404.
        """
        url = get_url("/promocode_my/apply/")
        response = requests.get(
            url,
            params={"code": "INVALID_XYZ_QA_9999"},
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал на невалидном промокоде. Ответ: {response.text[:300]}"
        assert response.status_code in [400, 404], \
            f"Невалидный промокод принят! Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 09.6 ──────────────────────────────────────────────────────────────
    def test_apply_promo_no_code_param(self):
        """
        Применение промокода без параметра code → 400.
        """
        url = get_url("/promocode_my/apply/")
        response = requests.get(url, headers=get_auth_headers())

        assert response.status_code != 500, \
            f"Сервер упал без параметра code. Ответ: {response.text[:300]}"
        assert response.status_code == 400, \
            f"Запрос без code принят! Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 09.8 ──────────────────────────────────────────────────────────────
    @pytest.mark.xfail(reason="BUG: DELETE несуществующего промокода возвращает 200 вместо 404", strict=True)
    def test_remove_nonexistent_promo(self):
        """
        Удаление несуществующего промокода из избранного → 404.
        """
        url = get_url("/promocode_my/999999/remove_favorite/")
        response = requests.delete(url, headers=get_auth_headers())

        assert response.status_code != 500, \
            f"Сервер упал. Ответ: {response.text[:300]}"
        assert response.status_code in [400, 404], \
            f"Ожидали 404. Статус: {response.status_code}"

    # ── 09.9 ──────────────────────────────────────────────────────────────
    def test_apply_empty_code(self):
        """
        Пустой промокод → не 500. Сервер должен вернуть ошибку валидации.
        """
        url = get_url("/promocode_my/apply/")
        response = requests.get(
            url,
            params={"code": ""},
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал на пустом коде. Ответ: {response.text[:300]}"

    # ── 09.10 ─────────────────────────────────────────────────────────────
    def test_apply_very_long_code(self):
        """
        Очень длинный промокод (200 символов) → не 500.
        """
        url = get_url("/promocode_my/apply/")
        response = requests.get(
            url,
            params={"code": "A" * 200},
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал на длинном коде. Ответ: {response.text[:300]}"

    # ── 09.11 ─────────────────────────────────────────────────────────────
    def test_apply_sql_injection_in_code(self):
        """
        SQL-инъекция в промокоде → не 500.
        """
        url = get_url("/promocode_my/apply/")
        response = requests.get(
            url,
            params={"code": "' OR '1'='1"},
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал на SQL-инъекции! Ответ: {response.text[:300]}"

    # ── 09.3 + 09.4 ───────────────────────────────────────────────────────
    def test_add_and_remove_promo_favorite(self):
        """
        Добавление промокода в избранное и удаление.
        Если промокод истёк — тест помечаем как xfail.
        """
        # Добавляем
        add_url = get_url("/promocode_my/add_favorite/")
        add_response = requests.post(
            add_url,
            json={"code": PROMO_CODE},
            headers=get_auth_headers(),
        )
        assert add_response.status_code != 500, \
            f"Сервер упал при добавлении. Ответ: {add_response.text[:300]}"

        if add_response.status_code not in [200, 201]:
            pytest.skip(f"Промокод {PROMO_CODE} недоступен. Статус: {add_response.status_code}")

        # Получаем promo_id из списка
        list_url = get_url("/promocode_my/favorites/")
        list_response = requests.get(list_url, headers=get_auth_headers())
        assert list_response.status_code == 200

        data = list_response.json().get("data", [])
        assert len(data) > 0, "Промокод добавлен, но список пустой"

        promo_id = data[0].get("id")
        assert promo_id is not None, "Нет поля id в промокоде"

        # Удаляем
        del_url = get_url(f"/promocode_my/{promo_id}/remove_favorite/")
        del_response = requests.delete(del_url, headers=get_auth_headers())

        assert del_response.status_code != 500, \
            f"Сервер упал при удалении. Ответ: {del_response.text[:300]}"
        assert del_response.status_code in [200, 204], \
            f"Промокод не удалился. Статус: {del_response.status_code}"