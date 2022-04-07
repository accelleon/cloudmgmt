from typing import Dict
from urllib.parse import urlparse, parse_qs

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.tests.utils import random_password, random_username, random_invalid_password
from app.core.config import configs
from app.tests.utils.user import (
    create_random_user,
    user_authenticate_headers,
)


def test_search_user(
    db: Session,
    admin_token_headers: Dict[str, str],
    client: TestClient,
) -> None:
    username, _, _ = create_random_user(db)
    r = client.get(
        f"{configs.API_V1_STR}/users",
        headers=admin_token_headers,
        params={
            "username": username,
            "page": 0,
            "per_page": 10,
        },
    )
    if not r.ok:
        print(r.json())
    resp = r.json()
    assert resp["total"] == 1
    assert resp["results"][0]["username"] == username


def test_partial_search(
    db: Session,
    admin_token_headers: Dict[str, str],
    client: TestClient,
) -> None:
    username, _, id = create_random_user(db)
    r = client.get(
        f"{configs.API_V1_STR}/users",
        headers=admin_token_headers,
        params={
            "username": username[:6],
            "page": 0,
            "per_page": 10,
        },
    )
    assert r.status_code == 200
    json = r.json()
    usernames = [u["username"] for u in json["results"]]
    assert json["total"]
    assert username in usernames
    assert configs.FIRST_USER_NAME not in usernames


def test_search_admins(
    admin_token_headers: Dict[str, str],
    client: TestClient,
) -> None:
    r = client.get(
        f"{configs.API_V1_STR}/users",
        headers=admin_token_headers,
        params={
            "is_admin": True,
            "page": 0,
            "per_page": 10,
        },
    )
    assert r.status_code == 200
    for u in r.json()["results"]:
        assert u["is_admin"]


def test_search_not_admins(
    admin_token_headers: Dict[str, str],
    client: TestClient,
) -> None:
    r = client.get(
        f"{configs.API_V1_STR}/users",
        headers=admin_token_headers,
        params={
            "is_admin": False,
            "page": 0,
            "per_page": 10,
        },
    )
    assert r.status_code == 200
    for u in r.json()["results"]:
        assert not u["is_admin"]


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
        f"{configs.API_V1_STR}/me",
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
