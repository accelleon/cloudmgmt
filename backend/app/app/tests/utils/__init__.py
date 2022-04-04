import random
import string
from typing import Dict

from fastapi.testclient import TestClient

from app.core.config import configs
from app.core.validators import validate_password


def random_password() -> str:
    while True:
        ret = "".join(
            random.choices(
                string.ascii_lowercase
                + string.ascii_uppercase
                + string.digits
                + "@$!%*?&",
                k=32,
            )
        )
        try:
            return validate_password(ret)
        except ValueError:
            pass


def random_invalid_password() -> str:
    return "".join(
        random.choices(
            string.ascii_lowercase + string.ascii_uppercase + string.digits, k=32
        )
    )


def random_username() -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits + "._-", k=16))


def get_superuser_token_headers(client: TestClient) -> Dict[str, str]:
    login_data = {
        "username": configs.FIRST_USER_NAME,
        "password": configs.FIRST_USER_PASS,
    }
    r = client.post(f"{configs.API_V1_STR}/login", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
