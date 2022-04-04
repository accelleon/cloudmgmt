from typing import Dict, Union
from urllib.parse import urlparse, parse_qs

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pyotp

from app.tests.utils import random_password, random_username, random_invalid_password
from app.core.config import configs
from app.tests.utils.user import (
    create_random_user,
    create_user_twofa,
    user_authenticate_headers,
    auth_headers_username,
)


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
    # Got the right user?
    assert user["username"] == login_data["username"]
    assert user["is_admin"]
    # Not leaking data
    assert "password" not in user


def test_update_me(
    db: Session,
    client: TestClient,
) -> None:
    username = random_username()
    new_pass = random_password()
    headers = auth_headers_username(db, client, username)
    update_data = {
        "password": new_pass,
    }
    r = client.post(f"{configs.API_V1_STR}/users/me", headers=headers, json=update_data)
    user = r.json()
    # Don't update things we didn't ask to
    assert user["username"] == username

    login_data = {
        "username": username,
        "password": new_pass,
    }
    r = client.post(f"{configs.API_V1_STR}/login", json=login_data)
    js = r.json()
    # Ensure new password is accepted
    assert r.status_code == 200
    assert "access_token" in js
    assert js["access_token"]


def test_enable_twofa(
    db: Session,
    client: TestClient,
) -> None:
    username, password, _ = create_random_user(db)
    headers = user_authenticate_headers(client, username, password)
    update_data: Dict[str, Union[str, bool]] = {
        "twofa_enabled": True,
    }
    r = client.post(f"{configs.API_V1_STR}/users/me", headers=headers, json=update_data)
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
    r = client.post(f"{configs.API_V1_STR}/users/me", headers=headers, json=update_data)
    user = r.json()
    # Make sure update was successful, twofa *was* enabled and we wiped the secret
    assert r.status_code == 200
    assert user["twofa_enabled"]
    assert not user["twofa_uri"]


def test_disable_twofa(
    db: Session,
    client: TestClient,
) -> None:
    username, password, secret = create_user_twofa(db)
    headers = user_authenticate_headers(
        client, username, password, pyotp.TOTP(secret).now()
    )
    update_data = {
        "twofa_enabled": False,
    }
    r = client.post(f"{configs.API_V1_STR}/users/me", headers=headers, json=update_data)
    user = r.json()
    # Make sure update was successful and 2fa was disabled
    assert r.status_code == 200
    assert not user["twofa_enabled"]
    # Try normal login
    headers = user_authenticate_headers(client, username, password)


def test_search_user(
    admin_token_headers: Dict[str, str],
    client: TestClient,
) -> None:
    r = client.get(
        f"{configs.API_V1_STR}/users",
        headers=admin_token_headers,
        params={
            "username": configs.FIRST_USER_NAME,
            "page": 0,
            "per_page": 10,
        },
    )
    if not r.ok:
        print(r.json())
    resp = r.json()
    assert resp["total"] == 1
    assert resp["results"][0]["username"] == configs.FIRST_USER_NAME


def test_search_links(
    admin_token_headers: Dict[str, str],
    client: TestClient,
) -> None:
    r = client.get(
        f"{configs.API_V1_STR}/users",
        headers=admin_token_headers,
        params={
            "page": 1,
            "per_page": 10,
        },
    )
    resp = r.json()
    assert r.status_code == 200
    assert "next" in resp
    assert "prev" in resp

    next = urlparse(resp["next"])
    nextQ = parse_qs(next.query)
    assert nextQ["page"][0] == "2"
    assert nextQ["per_page"][0] == "10"

    prev = urlparse(resp["prev"])
    prevQ = parse_qs(prev.query)
    assert prevQ["page"][0] == "0"
    assert prevQ["per_page"][0] == "10"


def test_search_not_admin(
    db: Session,
    client: TestClient,
) -> None:
    username, password, _ = create_random_user(db)
    headers = user_authenticate_headers(client, username, password)
    r = client.get(
        f"{configs.API_V1_STR}/users",
        headers=headers,
        params={
            "username": configs.FIRST_USER_NAME,
            "page": 0,
            "per_page": 10,
        },
    )
    assert r.status_code == 403


def test_create_user(
    admin_token_headers: Dict[str, str],
    client: TestClient,
) -> None:
    r = client.post(
        f"{configs.API_V1_STR}/users",
        headers=admin_token_headers,
        json={
            "username": random_username(),
            "password": random_password(),
            "first_name": "",
            "last_name": "",
        },
    )
    assert r.status_code == 201
    assert "id" in r.json()


def test_create_duplicate(
    admin_token_headers: Dict[str, str],
    client: TestClient,
) -> None:
    username = random_username()
    r = client.post(
        f"{configs.API_V1_STR}/users",
        headers=admin_token_headers,
        json={
            "username": username,
            "password": random_password(),
            "first_name": "",
            "last_name": "",
        },
    )
    assert r.status_code == 201
    r = client.post(
        f"{configs.API_V1_STR}/users",
        headers=admin_token_headers,
        json={
            "username": username,
            "password": random_password(),
            "first_name": "",
            "last_name": "",
        },
    )
    assert r.status_code == 409


def test_get_user(
    db: Session,
    admin_token_headers: Dict[str, str],
    client: TestClient,
) -> None:
    username, _, id = create_random_user(db)
    r = client.get(
        f"{configs.API_V1_STR}/users/{id}",
        headers=admin_token_headers,
    )
    assert r.status_code == 200
    assert r.json()["username"] == username


def test_create_invalid_password(
    admin_token_headers: Dict[str, str],
    client: TestClient,
) -> None:
    r = client.post(
        f"{configs.API_V1_STR}/users",
        headers=admin_token_headers,
        json={
            "username": random_username(),
            "password": random_invalid_password(),
            "first_name": "",
            "last_name": "",
        },
    )
    assert r.status_code == 422


def test_update_user(
    db: Session,
    admin_token_headers: Dict[str, str],
    client: TestClient,
) -> None:
    username, _, id = create_random_user(db)
    update_data = {
        "first_name": "test",
        "last_name": "test",
    }
    r = client.patch(
        f"{configs.API_V1_STR}/users/{id}",
        headers=admin_token_headers,
        json=update_data,
    )
    assert r.status_code == 200
    user = r.json()
    assert user["first_name"] == "test"
    assert user["last_name"] == "test"


def test_no_update_self(
    admin_token_headers: Dict[str, str],
    client: TestClient,
) -> None:
    r = client.get(
        f"{configs.API_V1_STR}/users/me",
        headers=admin_token_headers,
    )
    user = r.json()
    update_data = {
        "first_name": "test",
        "last_name": "test",
    }
    r = client.patch(
        f"{configs.API_V1_STR}/users/{user['id']}",
        headers=admin_token_headers,
        json=update_data,
    )
    assert r.status_code == 403


def test_delete_user(
    db: Session,
    admin_token_headers: Dict[str, str],
    client: TestClient,
) -> None:
    username, _, id = create_random_user(db)
    r = client.delete(
        f"{configs.API_V1_STR}/users/{id}",
        headers=admin_token_headers,
    )
    assert r.status_code == 204

    r = client.get(
        f"{configs.API_V1_STR}/users{id}",
        headers=admin_token_headers,
        params={
            "username": username,
        },
    )
    assert r.status_code == 404
