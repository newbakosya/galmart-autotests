import requests
import pytest
from config import get_url, get_auth_headers


class TestActions:
    # тесты регистрации чека — папка 12

    def test_promotions_list(self):
        # список акций — пустой список ок
        url = get_url("/actions/registration/")
        resp = requests.get(url, headers=get_auth_headers())
        assert resp.status_code == 200, f"список акций недоступен, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_user_actions(self):
        # история регистраций — на тестовом аккаунте может быть 404
        url = get_url("/actions/user/")
        resp = requests.get(url, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code in [200, 404], f"акции пользователя недоступны, статус: {resp.status_code}"

    def test_user_actions_no_auth(self):
        url = get_url("/actions/user/")
        resp = requests.get(url, headers={"Content-Type": "application/json"})
        assert resp.status_code == 401, f"акции доступны без токена! статус: {resp.status_code}"

    def test_register_receipt_empty_body(self):
        # пустое тело — 400
        url = get_url("/actions/registration/")
        resp = requests.post(url, json={}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code == 400, f"пустое тело принято! статус: {resp.status_code}"

    def test_register_receipt_no_auth(self):
        url = get_url("/actions/registration/")
        resp = requests.post(url, json={"action_id": "1", "receipt_code": "TEST"}, headers={"Content-Type": "application/json"})
        assert resp.status_code == 401, f"регистрация без токена прошла! статус: {resp.status_code}"

    def test_register_receipt_invalid_code(self):
        # код 'ABC' слишком короткий — должна быть валидация
        url = get_url("/actions/registration/")
        resp = requests.post(
            url,
            json={"action_id": "1", "receipt_code": "ABC", "first_name": "QA", "last_name": "Test"},
            headers=get_auth_headers(),
        )
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code in [400, 404], f"невалидный код принят! статус: {resp.status_code}"

    def test_register_receipt_digits_in_name(self):
        # цифры и символы в имени — 400
        url = get_url("/actions/registration/")
        resp = requests.post(
            url,
            json={"action_id": "1", "receipt_code": "TEST12345", "first_name": "12345", "last_name": "@@@"},
            headers=get_auth_headers(),
        )
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code in [400, 404], f"цифры в имени приняты! статус: {resp.status_code}"

    def test_register_receipt_very_long_code(self):
        # 150 символов в коде — не 500
        url = get_url("/actions/registration/")
        resp = requests.post(url, json={"action_id": "1", "receipt_code": "X" * 150}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал на длинном коде, ответ: {resp.text[:200]}"
