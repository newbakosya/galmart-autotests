import requests
import pytest
from config import get_url, get_auth_headers, get_full_headers, CITY_ID


class TestReferences:
    # тесты справочников — папка 13
    # большинство эндпоинтов публичные

    def test_shops_list(self):
        url = get_url("/addits/shops/")
        resp = requests.get(url, headers=get_auth_headers())
        assert resp.status_code == 200, f"список магазинов недоступен, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_shops_list_with_city_header(self):
        # с city header должно работать так же
        url = get_url("/addits/shops/")
        resp = requests.get(url, headers=get_full_headers())
        assert resp.status_code == 200, f"список магазинов с city header недоступен, статус: {resp.status_code}"

    def test_contacts(self):
        url = get_url("/addits/contact/")
        resp = requests.get(url, headers=get_auth_headers())
        assert resp.status_code == 200, f"контакты недоступны, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_faq(self):
        url = get_url("/addits/questions/")
        resp = requests.get(url, headers=get_auth_headers())
        assert resp.status_code == 200, f"faq недоступен, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_legal_documents(self):
        url = get_url("/addits/legal/")
        resp = requests.get(url, headers=get_auth_headers())
        assert resp.status_code == 200, f"юридические документы недоступны, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    def test_app_context(self):
        url = get_url("/addits/context/")
        resp = requests.get(url, headers=get_auth_headers())
        assert resp.status_code == 200, f"app context недоступен, статус: {resp.status_code}, ответ: {resp.text[:200]}"

    @pytest.mark.xfail(reason="BUG: /addits/check_version/ возвращает 404 на stage", strict=True)
    def test_check_version_ios(self):
        url = get_url("/addits/check_version/ios/1.0.0/")
        resp = requests.get(url, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code == 200, f"проверка версии ios недоступна, статус: {resp.status_code}"

    @pytest.mark.xfail(reason="BUG: /addits/check_version/ возвращает 404 на stage", strict=True)
    def test_check_version_android_outdated(self):
        # устаревшая версия — должен вернуть 200 с флагом update_required
        url = get_url("/addits/check_version/android/0.0.1/")
        resp = requests.get(url, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал, ответ: {resp.text[:200]}"
        assert resp.status_code == 200, f"проверка версии android недоступна, статус: {resp.status_code}"

    def test_check_version_invalid_format(self):
        # 'abc' вместо 'x.y.z' — не 500
        url = get_url("/addits/check_version/android/abc/")
        resp = requests.get(url, headers=get_auth_headers())
        assert resp.status_code != 500, f"сервер упал на невалидном формате версии, ответ: {resp.text[:200]}"
