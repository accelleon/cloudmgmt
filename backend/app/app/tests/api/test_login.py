from typing import Dict

from fastapi.testclient import TestClient

from app.core.config import configs


def test_get_access_token(client: TestClient) -> None:
    login_data = {
        "username": configs.FIRST_USER_NAME,
        "password": configs.FIRST_USER_PASS,
    }
    print(f"{configs.API_V1_STR}/login")
    r = client.post(f"{configs.API_V1_STR}/login", json=login_data)
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]
