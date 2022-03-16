from typing import Dict

from fastapi.testclient import TestClient
import pyotp

from app.tests.utils import random_lower_string
from app.core.config import configs


def test_get_me(client: TestClient) -> None:
    login_data = {
        "username": configs.FIRST_USER_NAME,
        "password": configs.FIRST_USER_PASS,
    }
    r = client.post(f"{configs.API_V1_STR}/login", json=login_data)
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get(f"{configs.API_V1_STR}/users/me", headers=headers)
    user = r.json()
    assert user["username"] == login_data["username"]
    assert user["is_admin"]


def test_update_me(client: TestClient) -> None:
    pass