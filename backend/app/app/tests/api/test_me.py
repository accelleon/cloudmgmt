from typing import Dict, Union
from urllib.parse import urlparse, parse_qs

import pytest
from httpx import AsyncClient as TestClient
from sqlalchemy.ext.asyncio import AsyncSession as Session
import pyotp

from app.tests.utils import random_password
from app.core.config import configs
from app.tests.utils.user import (
    create_random_user,
    create_user_twofa,
    user_authenticate_headers,
)


@pytest.mark.asyncio
async def test_get_me(client: TestClient) -> None:
    login_data = {
        "username": configs.FIRST_USER_NAME,
        "password": configs.FIRST_USER_PASS,
    }
    r = await client.post(f"{configs.API_V1_STR}/login", json=login_data)
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    r = await client.get(f"{configs.API_V1_STR}/me", headers=headers)
    user = r.json()
    # Got the right user?
    assert user["username"] == login_data["username"]
    assert user["is_admin"]
    # Not leaking data
    assert "password" not in user


@pytest.mark.asyncio
async def test_update_me(
    db: Session,
    client: TestClient,
) -> None:
    new_pass = random_password()
    username, password, _ = await create_random_user(db)
    headers = await user_authenticate_headers(client, username, password)
    update_data = {
        "old_password": password,
        "password": new_pass,
    }
    r = await client.post(f"{configs.API_V1_STR}/me", headers=headers, json=update_data)
    user = r.json()
    # Don't update things we didn't ask to
    print(r.json())
    assert r.status_code == 200
    assert user["username"] == username

    login_data = {
        "username": username,
        "password": new_pass,
    }
    r = await client.post(f"{configs.API_V1_STR}/login", json=login_data)
    js = r.json()
    # Ensure new password is accepted
    assert r.status_code == 200
    assert "access_token" in js
    assert js["access_token"]


@pytest.mark.asyncio
async def test_update_wrong_pass(
    db: Session,
    client: TestClient,
) -> None:
    username, password, _ = await create_random_user(db)
    headers = await user_authenticate_headers(client, username, password)
    update_data = {
        "old_password": random_password(),
        "password": random_password(),
    }
    r = await client.post(f"{configs.API_V1_STR}/me", headers=headers, json=update_data)
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_update_same_pass(
    db: Session,
    client: TestClient,
) -> None:
    username, password, _ = await create_random_user(db)
    headers = await user_authenticate_headers(client, username, password)
    update_data = {
        "old_password": password,
        "password": password,
    }
    r = await client.post(f"{configs.API_V1_STR}/me", headers=headers, json=update_data)
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_enable_twofa(
    db: Session,
    client: TestClient,
) -> None:
    username, password, _ = await create_random_user(db)
    headers = await user_authenticate_headers(client, username, password)
    update_data: Dict[str, Union[str, bool]] = {
        "twofa_enabled": True,
    }
    r = await client.post(f"{configs.API_V1_STR}/me", headers=headers, json=update_data)
    user = r.json()
    # Make sure update was successful, received a secret and 2fa isn't marked enabled yet
    assert r.status_code == 200
    assert "twofa_uri" in user
    assert user["twofa_uri"]

    uri = urlparse(user["twofa_uri"])
    secret = parse_qs(uri.query)["secret"][0]

    # Generate a 2fa response code and send again
    totp = pyotp.TOTP(secret)
    update_data = {"twofa_enabled": True, "twofa_code": totp.now()}
    r = await client.post(f"{configs.API_V1_STR}/me", headers=headers, json=update_data)
    user = r.json()
    # Make sure update was successful, twofa *was* enabled and we wiped the secret
    assert r.status_code == 200
    assert user["twofa_enabled"]
    assert not user["twofa_uri"]


@pytest.mark.asyncio
async def test_disable_twofa(
    db: Session,
    client: TestClient,
) -> None:
    username, password, secret = await create_user_twofa(db)
    headers = await user_authenticate_headers(
        client, username, password, pyotp.TOTP(secret).now()
    )
    update_data = {
        "twofa_enabled": False,
    }
    r = await client.post(f"{configs.API_V1_STR}/me", headers=headers, json=update_data)
    user = r.json()
    # Make sure update was successful and 2fa was disabled
    assert r.status_code == 200
    assert not user["twofa_enabled"]
    # Try normal login
    headers = await user_authenticate_headers(client, username, password)
