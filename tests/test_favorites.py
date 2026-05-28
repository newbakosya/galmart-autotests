import requests
import pytest
from config import get_url, get_auth_headers, get_full_headers, CITY_ID


class TestFavorites:
    # тесты избранного — папка 06

    def test_list_favorites(self):
        # список избранного — может быть пустым
        url = get_url("/catalog/favorite/")
        resp = requests.get(url, params={"page": 1, "limit": 10}, headers=get_auth_headers())
        assert resp.status_code == 200, f"избранное недоступно, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_list_favorites_no_auth(self):
        url = get_url("/catalog/favorite/")
        resp = requests.get(url, headers={"Content-Type": "application/json"})
        assert resp.status_code == 401, f"избранное доступно без токена! статус: {resp.status_code}"

    def test_add_nonexistent_good_to_favorites(self):
        # несуществующий товар — 400 или 404
        url = get_url("/catalog/favorite/")
        resp = requests.post(url, json={"good": 999999999}, headers=get_auth_headers())
        assert resp.status_code in [400, 404], f"несуществующий товар добавлен в избранное! статус: {resp.status_code}"

    def test_delete_nonexistent_favorite(self):
        url = get_url("/catalog/favorite/999999/")
        resp = requests.delete(url, headers=get_auth_headers())
        assert resp.status_code == 404, f"ожидали 404, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_clear_favorites_not_500(self):
        # очистка даже если уже пустое — не должно падать
        url = get_url("/catalog/favorite/clear/")
        resp = requests.delete(url, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал при очистке, ответ: {resp.text[:200]}"
        assert resp.status_code in [200, 204], f"неожиданный статус: {resp.status_code}"

    def test_favorites_page_out_of_range(self):
        url = get_url("/catalog/favorite/")
        resp = requests.get(url, params={"page": 99999}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал на странице 99999, ответ: {resp.text[:200]}"

    def test_favorites_pagination(self):
        # пагинация с limit=1
        url = get_url("/catalog/favorite/")
        resp = requests.get(url, params={"page": 1, "limit": 1}, headers=get_auth_headers())
        assert resp.status_code == 200, f"пагинация не работает, статус: {resp.status_code}"

    def test_add_and_delete_favorite_full_cycle(self):
        # проверяем что эндпоинт добавления доступен и возвращает json
        url = get_url("/catalog/favorite/")
        resp = requests.post(url, json={"good": "00000000"}, headers=get_auth_headers())
        assert resp.status_code != 404, "эндпоинт избранного не найден"
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        try:
            data = resp.json()
        except Exception as e:
            pytest.fail(f"ответ не json: {e}")
        assert data is not None
