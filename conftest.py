import pytest
import requests
import os
from config import ACCESS_TOKEN, CITY_ID


@pytest.fixture(scope="session")
def session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    yield s
    s.close()


@pytest.fixture(scope="session")
def auth_headers():
    if not ACCESS_TOKEN:
        pytest.skip(
            "ACCESS_TOKEN не задан в .env. "
            "Получи токен через Postman (01.1 + 01.2) и вставь в .env"
        )
    return {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }


@pytest.fixture(scope="session")
def city_headers():
    return {
        "City": CITY_ID,
        "Content-Type": "application/json",
    }


@pytest.fixture(scope="session")
def full_headers(auth_headers, city_headers):
    return {**auth_headers, **city_headers}