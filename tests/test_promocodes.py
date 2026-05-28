import requests
import pytest
from config import get_url, get_auth_headers

PROMO_CODE = "TESTPROMO"


class TestPromocodes:
    # тесты промокодов — папка 09

    def test_list_favorite_promos(self):
        url = get_url("/promocode_my/favorites/")
        resp = requests.get(url, headers=get_auth_headers())
        assert resp.status_code == 200, f"список промокодов недоступен, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_list_promos_no_auth(self):
        url = get_url("/promocode_my/favorites/")
        resp = requests.get(url, headers={"Content-Type": "application/json"})
        assert resp.status_code == 401, f"промокоды доступны без токена! статус: {resp.status_code}"

    def test_apply_invalid_promo(self):
        url = get_url("/promocode_my/apply/")
        resp = requests.get(url, params={"code": "INVALID_XYZ_QA_9999"}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code in [400, 404], f"невалидный промокод принят! статус: {resp.status_code}"

    def test_apply_promo_no_code_param(self):
        # без параметра code — 400
        url = get_url("/promocode_my/apply/")
        resp = requests.get(url, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code == 400, f"запрос без code принят! статус: {resp.status_code}"

    @pytest.mark.xfail(reason="BUG: DELETE несуществующего промокода возвращает 200 вместо 404", strict=True)
    def test_remove_nonexistent_promo(self):
        url = get_url("/promocode_my/999999/remove_favorite/")
        resp = requests.delete(url, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code in [400, 404], f"ожидали 404, статус: {resp.status_code}"

    def test_apply_empty_code(self):
        url = get_url("/promocode_my/apply/")
        resp = requests.get(url, params={"code": ""}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал на пустом коде, ответ: {resp.text[:200]}"

    def test_apply_very_long_code(self):
        # 200 символов — не должно быть 500
        url = get_url("/promocode_my/apply/")
        resp = requests.get(url, params={"code": "A" * 200}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал на длинном коде, ответ: {resp.text[:200]}"

    def test_apply_sql_injection_in_code(self):
        url = get_url("/promocode_my/apply/")
        resp = requests.get(url, params={"code": "' OR '1'='1"}, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал на sql инъекции! ответ: {resp.text[:200]}"

    def test_add_and_remove_promo_favorite(self):
        # полный цикл: добавить и удалить промокод из избранного
        add_url = get_url("/promocode_my/add_favorite/")
        add_resp = requests.post(add_url, json={"code": PROMO_CODE}, headers=get_auth_headers())
        assert add_resp.status_code != 500, f"сервер упал при добавлении, ответ: {add_resp.text[:200]}"
        if add_resp.status_code not in [200, 201]:
            pytest.skip(f"промокод {PROMO_CODE} недоступен, статус: {add_resp.status_code}")
        # получаем promo_id
        list_resp = requests.get(get_url("/promocode_my/favorites/"), headers=get_auth_headers())
        assert list_resp.status_code == 200
        data = list_resp.json().get("data", [])
        assert len(data) > 0, "промокод добавлен, но список пустой"
        promo_id = data[0].get("id")
        assert promo_id is not None, "нет поля id в промокоде"
        # удаляем
        del_resp = requests.delete(get_url(f"/promocode_my/{promo_id}/remove_favorite/"), headers=get_auth_headers())
        assert del_resp.status_code != 500, f"сервер упал при удалении, ответ: {del_resp.text[:200]}"
        assert del_resp.status_code in [200, 204], f"промокод не удалился, статус: {del_resp.status_code}"
