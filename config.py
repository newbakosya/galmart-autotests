import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://test1.galmart.kz")
API_PREFIX = "/api/v2"
CITY_ID = os.getenv("CITY_ID", "6737")
PHONE = os.getenv("PHONE", "77785636893")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "")


def get_url(path: str) -> str:
    return f"{BASE_URL}{API_PREFIX}{path}"


def get_auth_headers() -> dict:
    return {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }


def get_city_headers() -> dict:
    return {
        "City": CITY_ID,
        "Content-Type": "application/json",
    }


def get_full_headers() -> dict:
    return {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "City": CITY_ID,
        "Content-Type": "application/json",
    }