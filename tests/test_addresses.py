import requests
import pytest
from config import get_url, get_auth_headers

# корректные данные для создания адреса
# важно: city=2 (астана fk) — отличается от city_id=6737 (city header)
# swagger ошибочно показывает city_id, реальное поле — city
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
    # тесты адресов — папка 04

    def test_list_addresses(self):
        # список адресов — может быть пустым
        url = get_url("/account/address/")
        resp = requests.get(url, headers=get_auth_headers())
        assert resp.status_code == 200, f"адреса недоступны, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_list_addresses_no_auth(self):
        url = get_url("/account/address/")
        resp = requests.get(url, headers={"Content-Type": "application/json"})
        assert resp.status_code == 401, f"адреса доступны без авторизации! статус: {resp.status_code}"

    def test_create_address_empty_body(self):
        # пустое тело — все поля обязательные
        url = get_url("/account/address/")
        resp = requests.post(url, json={}, headers=get_auth_headers())
        assert resp.status_code == 400, f"ожидали 400, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_create_address_missing_name(self):
        # без поля name — 400
        url = get_url("/account/address/")
        body = {k: v for k, v in VALID_ADDRESS.items() if k != "name"}
        resp = requests.post(url, json=body, headers=get_auth_headers())
        assert resp.status_code == 400, f"ожидали 400, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_create_address_missing_latitude(self):
        # без координат — 400
        url = get_url("/account/address/")
        body = {k: v for k, v in VALID_ADDRESS.items() if k not in ["latitude", "longitude"]}
        resp = requests.post(url, json=body, headers=get_auth_headers())
        assert resp.status_code == 400, f"ожидали 400, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_create_address_swagger_wrong_fields(self):
        # swagger показывает lat/lon/city_id, но реальное апи ждёт latitude/longitude/city
        url = get_url("/account/address/")
        resp = requests.post(
            url,
            json={"name": "Bug048", "address": "Тест", "city_id": 6737, "building": "1", "lat": 51.18, "lon": 71.44},
            headers=get_auth_headers(),
        )
        assert resp.status_code == 400, f"swagger-поля прошли валидацию — документация некорректна, статус: {resp.status_code}"

    def test_delete_nonexistent_address(self):
        url = get_url("/account/address/999999/")
        resp = requests.delete(url, headers=get_auth_headers())
        assert resp.status_code == 404, f"ожидали 404, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_update_nonexistent_address(self):
        url = get_url("/account/address/999999/")
        resp = requests.put(url, json=VALID_ADDRESS, headers=get_auth_headers())
        assert resp.status_code == 404, f"ожидали 404, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_get_address_by_id_returns_405(self):
        # баг: get по конкретному id возвращает 405 вместо 200
        url = get_url("/account/address/1/")
        resp = requests.get(url, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code in [200, 404, 405], f"неожиданный статус: {resp.status_code}"

    def test_create_address_invalid_coords(self):
        # невалидные координаты — не должно быть 500
        url = get_url("/account/address/")
        body = {**VALID_ADDRESS, "latitude": 9999, "longitude": 9999}
        resp = requests.post(url, json=body, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал на невалидных координатах, ответ: {resp.text[:200]}"

    @pytest.mark.parametrize("method", ["PUT", "PATCH", "DELETE"])
    def test_idor_other_user_address(self, method):
        # idor: пробуем изменить/удалить чужой адрес (id 27454)
        # ожидаем 403 или 404, но не 200 — это была бы уязвимость
        url = get_url("/account/address/27454/")
        if method == "PUT":
            resp = requests.put(url, json=VALID_ADDRESS, headers=get_auth_headers())
        elif method == "PATCH":
            resp = requests.patch(url, json={"comment": "idor test"}, headers=get_auth_headers())
        else:
            resp = requests.delete(url, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал на idor тесте ({method}), ответ: {resp.text[:200]}"
        assert resp.status_code != 200, f"idor уязвимость! {method} чужого адреса вернул 200"
