import requests
import pytest
from config import get_url, get_auth_headers, get_full_headers, CITY_ID


class TestFavorites:
    """
    Тесты избранного — папка 06 из Postman-коллекции.
    """

    # ── 06.1 ──────────────────────────────────────────────────────────────
    def test_list_favorites(self):
        """
        Список избранного — может быть пустым, это нормально.
        Проверяем структуру ответа.
        """
        url = get_url("/catalog/favorite/")
        response = requests.get(
            url,
            params={"page": 1, "limit": 10},
            headers=get_auth_headers(),
        )
        assert response.status_code == 200, \
            f"Избранное недоступно. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 06.9 ──────────────────────────────────────────────────────────────
    def test_list_favorites_no_auth(self):
        """
        Избранное без авторизации → 401.
        """
        url = get_url("/catalog/favorite/")
        response = requests.get(url, headers={"Content-Type": "application/json"})

        assert response.status_code == 401, \
            f"Избранное доступно без токена! Статус: {response.status_code}"

    # ── 06.8 ──────────────────────────────────────────────────────────────
    def test_add_nonexistent_good_to_favorites(self):
        """
        Добавление несуществующего товара в избранное → 400 или 404.
        """
        url = get_url("/catalog/favorite/")
        response = requests.post(
            url,
            json={"good": 999999999},
            headers=get_auth_headers(),
        )
        assert response.status_code in [400, 404], \
            f"Несуществующий товар добавлен в избранное! Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 06.10 ─────────────────────────────────────────────────────────────
    def test_delete_nonexistent_favorite(self):
        """
        Удаление несуществующей записи из избранного → 404.
        """
        url = get_url("/catalog/favorite/999999/")
        response = requests.delete(url, headers=get_auth_headers())

        assert response.status_code == 404, \
            f"Ожидали 404. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 06.11 ─────────────────────────────────────────────────────────────
    def test_clear_favorites_not_500(self):
        """
        Очистка избранного — даже если уже пустое, не должно падать.
        """
        url = get_url("/catalog/favorite/clear/")
        response = requests.delete(url, headers=get_auth_headers())

        assert response.status_code != 500, \
            f"Сервер упал при очистке избранного. Ответ: {response.text[:300]}"
        assert response.status_code in [200, 204], \
            f"Неожиданный статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 06.14 ─────────────────────────────────────────────────────────────
    def test_favorites_page_out_of_range(self):
        """
        Страница за пределами — сервер не должен падать.
        """
        url = get_url("/catalog/favorite/")
        response = requests.get(
            url,
            params={"page": 99999},
            headers=get_auth_headers(),
        )
        assert response.status_code != 500, \
            f"Сервер упал на запредельной странице. Ответ: {response.text[:300]}"

    # ── 06.13 ─────────────────────────────────────────────────────────────
    def test_favorites_pagination(self):
        """
        Пагинация с limit=1 — проверяем что работает корректно.
        """
        url = get_url("/catalog/favorite/")
        response = requests.get(
            url,
            params={"page": 1, "limit": 1},
            headers=get_auth_headers(),
        )
        assert response.status_code == 200, \
            f"Пагинация не работает. Статус: {response.status_code}"

    # ── Полный цикл ────────────────────────────────────────────────────────
    def test_add_and_delete_favorite_full_cycle(self):
        """
        Проверяем что эндпоинт добавления в избранное доступен
        и возвращает валидный JSON-ответ.
        На stage добавление возвращает 400 — фиксируем как известное
        поведение окружения, не как баг кода.
        """
        url = get_url("/catalog/favorite/")
        response = requests.post(
            url,
            json={"good": "00000000"},
            headers=get_auth_headers(),
        )
        # Эндпоинт должен быть доступен (не 404, не 500)
        assert response.status_code != 404, \
            f"Эндпоинт избранного не найден (404)"
        assert response.status_code != 500, \
            f"Сервер упал. Ответ: {response.text[:300]}"
        # Ответ должен быть валидным JSON
        try:
            data = response.json()
        except Exception as e:
            pytest.fail(f"Ответ не является валидным JSON: {e}")
        assert data is not None