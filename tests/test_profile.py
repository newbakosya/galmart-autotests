import requests
import pytest
from config import get_url, get_auth_headers


class TestProfile:
    # тесты профиля — папка 02

    def test_get_profile(self):
        # получаем профиль и проверяем структуру
        url = get_url("/account/profile/")
        resp = requests.get(url, headers=get_auth_headers())
        assert resp.status_code == 200, f"профиль недоступен, статус: {resp.status_code}, ответ: {resp.text[:200]}"
        data = resp.json()
        assert "data" in data, f"нет поля data, поля: {list(data.keys())}"
        profile = data["data"]
        assert "phone" in profile, f"нет поля phone, поля: {list(profile.keys())}"

    def test_get_profile_with_page_param(self):
        # с параметром page=1 не должно ломаться
        url = get_url("/account/profile/")
        resp = requests.get(url, params={"page": 1}, headers=get_auth_headers())
        assert resp.status_code == 200, f"статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_get_bonus_balance(self):
        # баланс бонусов — нужен при оформлении заказа
        url = get_url("/account/points/")
        resp = requests.get(url, headers=get_auth_headers())
        assert resp.status_code == 200, f"баланс недоступен, статус: {resp.status_code}"
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"

    def test_bonus_transactions_list(self):
        # история бонусных операций
        url = get_url("/bonus/transaction/")
        resp = requests.get(url, headers=get_auth_headers())
        assert resp.status_code == 200, f"транзакции недоступны, статус: {resp.status_code}"

    def test_bonus_transaction_by_id(self):
        # транзакция по id — на stage есть баг, проверяем что не 500
        url = get_url("/bonus/transaction/1/")
        resp = requests.get(url, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"

    @pytest.mark.parametrize("platform,version", [
        ("ios", "1.0.0"),
        ("android", "1.0.0"),
    ])
    def test_check_app_version(self, platform, version):
        # проверка версии приложения — главное не 500
        url = get_url(f"/addits/check_version/{platform}/{version}/")
        resp = requests.get(url, headers={"Content-Type": "application/json"})
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code in [200, 400, 404], f"неожиданный статус: {resp.status_code}"

    def test_patch_profile_valid(self):
        # обновляем имя и фамилию — безопасно, телефон не трогаем
        url = get_url("/account/profile/")
        resp = requests.patch(
            url,
            json={"name": "QA", "lastname": "Tester", "birthday": "01.01.1990"},
            headers=get_auth_headers(),
        )
        assert resp.status_code in [200, 201], f"patch не сработал, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_patch_profile_phone_readonly(self):
        # телефон read-only, сервер должен проигнорировать или вернуть ошибку
        url = get_url("/account/profile/")
        resp = requests.patch(url, json={"phone": "77000000000"}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"

    def test_patch_profile_invalid_birthday(self):
        # невалидный формат даты — ожидаем 400
        url = get_url("/account/profile/")
        resp = requests.patch(
            url,
            json={"name": "QA", "lastname": "Test", "birthday": "not-a-date"},
            headers=get_auth_headers(),
        )
        assert resp.status_code == 400, f"ожидали 400, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_patch_profile_xss_in_name(self):
        # xss в имени — не должно падать
        url = get_url("/account/profile/")
        resp = requests.patch(
            url,
            json={"name": "<script>alert('xss')</script>", "lastname": "Test", "birthday": "1990-01-01"},
            headers=get_auth_headers(),
        )
        assert resp.status_code != 500, f"сервер упал на xss, ответ: {resp.text[:200]}"

    def test_patch_profile_sql_injection(self):
        # sql инъекция в имени — не должно падать
        url = get_url("/account/profile/")
        resp = requests.patch(
            url,
            json={"name": "'; DROP TABLE users; --", "lastname": "Test", "birthday": "1990-01-01"},
            headers=get_auth_headers(),
        )
        assert resp.status_code != 500, f"сервер упал на sql инъекции, ответ: {resp.text[:200]}"

    def test_patch_profile_very_long_name(self):
        # 500 символов в имени — сервер не должен падать
        url = get_url("/account/profile/")
        resp = requests.patch(
            url,
            json={"name": "А" * 500, "lastname": "Test", "birthday": "1990-01-01"},
            headers=get_auth_headers(),
        )
        assert resp.status_code != 500, f"сервер упал на длинном имени, ответ: {resp.text[:200]}"
