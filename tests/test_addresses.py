import requests
import pytest
from config import get_url, get_auth_headers

# Корректные данные для создания адреса
# Важно: city=2 (Астана FK) — отличается от city_id=6737 (City header)
# Swagger ошибочно показывает city_id, реальное поле — city
VALID_ADDRESS = {
    "name": "QA Test Address",
    "address": "Астана, Кабанбай батыра 10",
    "city": 2,
    "building": "10",
    "apartment": "1",
    "latitude": 51.1801,
    "longitude": 71.4460,
    "comment": "QA автотест"
}


class TestAddresses:
    """
    Тесты управления адресами — папка 04 из Postman-коллекции.
    """

    # ── 04.1 ──────────────────────────────────────────────────────────────
    def test_list_addresses(self):
        """
        Список адресов авторизованного пользователя.
        Может быть пустым — это нормально.
        """
        url = get_url("/account/address/")
        response = requests.get(url, headers=get_auth_headers())

        assert response.status_code == 200, \
            f"Адреса недоступны. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 04.12 ─────────────────────────────────────────────────────────────
    def test_list_addresses_no_auth(self):
        """
        Список адресов без авторизации → 401.
        """
        url = get_url("/account/address/")
        response = requests.get(url, headers={"Content-Type": "application/json"})

        assert response.status_code == 401, \
            f"Адреса доступны без авторизации! Статус: {response.status_code}"

    # ── 04.10 ─────────────────────────────────────────────────────────────
    def test_create_address_empty_body(self):
        """
        Создание адреса с пустым телом → 400.
        Все поля обязательные.
        """
        url = get_url("/account/address/")
        response = requests.post(
            url,
            json={},
            headers=get_auth_headers(),
        )
        assert response.status_code == 400, \
            f"Ожидали 400 на пустое тело. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 04.8 ──────────────────────────────────────────────────────────────
    def test_create_address_missing_name(self):
        """
        Создание адреса без обязательного поля name → 400.
        """
        url = get_url("/account/address/")
        body = {k: v for k, v in VALID_ADDRESS.items() if k != "name"}
        response = requests.post(url, json=body, headers=get_auth_headers())

        assert response.status_code == 400, \
            f"Ожидали 400 без name. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 04.9 ──────────────────────────────────────────────────────────────
    def test_create_address_missing_latitude(self):
        """
        Создание адреса без координат → 400.
        """
        url = get_url("/account/address/")
        body = {k: v for k, v in VALID_ADDRESS.items() if k not in ["latitude", "longitude"]}
        response = requests.post(url, json=body, headers=get_auth_headers())

        assert response.status_code == 400, \
            f"Ожидали 400 без координат. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 04.11 ─────────────────────────────────────────────────────────────
    def test_create_address_swagger_wrong_fields(self):
        """
        BUG-048: Swagger показывает поля lat/lon/city_id,
        но реальный API ожидает latitude/longitude/city.
        Проверяем что Swagger-поля возвращают ошибку.
        """
        url = get_url("/account/address/")
        response = requests.post(
            url,
            json={
                "name": "Bug048",
                "address": "Тест",
                "city_id": 6737,
                "building": "1",
                "lat": 51.18,
                "lon": 71.44
            },
            headers=get_auth_headers(),
        )
        assert response.status_code == 400, \
            f"Swagger-поля прошли валидацию — документация некорректна. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 04.13 ─────────────────────────────────────────────────────────────
    def test_delete_nonexistent_address(self):
        """
        Удаление несуществующего адреса → 404.
        """
        url = get_url("/account/address/999999/")
        response = requests.delete(url, headers=get_auth_headers())

        assert response.status_code == 404, \
            f"Ожидали 404. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 04.14 ─────────────────────────────────────────────────────────────
    def test_update_nonexistent_address(self):
        """
        Обновление несуществующего адреса → 404.
        """
        url = get_url("/account/address/999999/")
        response = requests.put(
            url,
            json=VALID_ADDRESS,
            headers=get_auth_headers(),
        )
        assert response.status_code == 404, \
            f"Ожидали 404. Статус: {response.status_code}. Ответ: {response.text[:300]}"

    # ── 04.7 ──────────────────────────────────────────────────────────────
    def test_get_address_by_id_returns_405(self):
        """
        BUG-047: GET /account/address/{id}/ возвращает 405 Method Not Allowed.
        Получение конкретного адреса по ID не поддерживается — это баг.
        """
        url = get_url("/account/address/1/")
        response = requests.get(url, headers=get_auth_headers())

        assert response.status_code != 500, \
            f"Сервер упал. Ответ: {response.text[:300]}"
        # фиксируем баг — 405 вместо 200
        assert response.status_code in [200, 404, 405], \
            f"Неожиданный статус: {response.status_code}"

    # ── 04.17 ─────────────────────────────────────────────────────────────
    def test_create_address_invalid_coords(self):
        """
        Невалидные координаты (широта 9999) → сервер не должен падать.
        """
        url = get_url("/account/address/")
        body = {**VALID_ADDRESS, "latitude": 9999, "longitude": 9999}
        response = requests.post(url, json=body, headers=get_auth_headers())

        assert response.status_code != 500, \
            f"Сервер упал на невалидных координатах. Ответ: {response.text[:300]}"

    # ── 04.18 / 04.19 / 04.20 ─────────────────────────────────────────────
    @pytest.mark.parametrize("method", ["PUT", "PATCH", "DELETE"])
    def test_idor_other_user_address(self, method):
        """
        IDOR тест: попытка изменить/удалить адрес другого пользователя.
        ID 27454 — из Postman-коллекции, принадлежит другому аккаунту.
        Ожидаем 403 или 404, но не 200 (это была бы уязвимость).
        """
        url = get_url("/account/address/27454/")
        if method == "PUT":
            response = requests.put(url, json=VALID_ADDRESS, headers=get_auth_headers())
        elif method == "PATCH":
            response = requests.patch(url, json={"comment": "IDOR test"}, headers=get_auth_headers())
        else:
            response = requests.delete(url, headers=get_auth_headers())

        assert response.status_code != 500, \
            f"Сервер упал на IDOR тесте ({method}). Ответ: {response.text[:300]}"
        assert response.status_code != 200, \
            f"IDOR УЯЗВИМОСТЬ! {method} чужого адреса вернул 200. Ответ: {response.text[:300]}"