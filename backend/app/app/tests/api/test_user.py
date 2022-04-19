from typing import Dict
from urllib.parse import urlparse, parse_qs

import pytest
from httpx import AsyncClient as TestClient
from sqlalchemy.ext.asyncio import AsyncSession as Session

from app.tests.utils import random_password, random_username, random_invalid_password
from app.core.config import configs
from app.tests.utils.user import (
    create_random_user,
    user_authenticate_headers,
)


@pytest.mark.asyncio
async def test_search_user(
    db: Session,
    admin_token_headers: Dict[str, str],
    client: TestClient,
) -> None:
    username, _, _ = await create_random_user(db)
    r = await client.get(
        f"{configs.API_V1_STR}/users",
        headers=admin_token_headers,
        params={
            "username": username,
            "page": 0,
            "per_page": 10,
        },
    )
    if r.status_code != 200:
        print(r.json())
    resp = r.json()
    assert resp["total"] == 1
    assert resp["results"][0]["username"] == username


@pytest.mark.asyncio
async def test_partial_search(
    db: Session,
    admin_token_headers: Dict[str, str],
    client: TestClient,
) -> None:
    username, _, _ = await create_random_user(db)
    r = await client.get(
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


@pytest.mark.asyncio
async def test_search_admins(
    admin_token_headers: Dict[str, str],
    client: TestClient,
) -> None:
    r = await client.get(
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


@pytest.mark.asyncio
async def test_search_not_admins(
    admin_token_headers: Dict[str, str],
    client: TestClient,
) -> None:
    r = await client.get(
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


@pytest.mark.asyncio
async def test_search_links(
    admin_token_headers: Dict[str, str],
    client: TestClient,
) -> None:
    r = await client.get(
        f"{configs.API_V1_STR}/users",
        headers=admin_token_headers,
        params={
            "page": 1,
            "per_page": 2,
        },
    )
    resp = r.json()
    assert r.status_code == 200
    assert "next" in resp
    assert "prev" in resp

    next = urlparse(resp["next"])
    nextQ = parse_qs(next.query)
    assert nextQ["page"][0] == "2"
    assert nextQ["per_page"][0] == "2"

    prev = urlparse(resp["prev"])
    prevQ = parse_qs(prev.query)
    assert prevQ["page"][0] == "0"
    assert prevQ["per_page"][0] == "2"


@pytest.mark.asyncio
async def test_search_not_admin(
    db: Session,
    client: TestClient,
) -> None:
    username, password, _ = await create_random_user(db)
    headers = await user_authenticate_headers(client, username, password)
    r = await client.get(
        f"{configs.API_V1_STR}/users",
        headers=headers,
        params={
            "username": configs.FIRST_USER_NAME,
            "page": 0,
            "per_page": 10,
        },
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_create_user(
    admin_token_headers: Dict[str, str],
    client: TestClient,
) -> None:
    r = await client.post(
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


@pytest.mark.asyncio
async def test_create_duplicate(
    admin_token_headers: Dict[str, str],
    client: TestClient,
) -> None:
    username = random_username()
    r = await client.post(
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
    r = await client.post(
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


@pytest.mark.asyncio
async def test_get_user(
    db: Session,
    admin_token_headers: Dict[str, str],
    client: TestClient,
) -> None:
    username, _, id = await create_random_user(db)
    r = await client.get(
        f"{configs.API_V1_STR}/users/{id}",
        headers=admin_token_headers,
    )
    assert r.status_code == 200
    assert r.json()["username"] == username


@pytest.mark.asyncio
async def test_create_invalid_password(
    admin_token_headers: Dict[str, str],
    client: TestClient,
) -> None:
    r = await client.post(
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


@pytest.mark.asyncio
async def test_create_invalid_username(
    admin_token_headers: Dict[str, str],
    client: TestClient,
) -> None:
    r = await client.post(
        f"{configs.API_V1_STR}/users",
        headers=admin_token_headers,
        json={
            "username": "asdfa$",
            "password": random_password(),
            "first_name": "",
            "last_name": "",
        },
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_update_user(
    db: Session,
    admin_token_headers: Dict[str, str],
    client: TestClient,
) -> None:
    username, _, id = await create_random_user(db)
    update_data = {
        "first_name": "test",
        "last_name": "test",
    }
    r = await client.patch(
        f"{configs.API_V1_STR}/users/{id}",
        headers=admin_token_headers,
        json=update_data,
    )
    assert r.status_code == 200
    user = r.json()
    assert user["first_name"] == "test"
    assert user["last_name"] == "test"


@pytest.mark.asyncio
async def test_no_update_self(
    admin_token_headers: Dict[str, str],
    client: TestClient,
) -> None:
    r = await client.get(
        f"{configs.API_V1_STR}/me",
        headers=admin_token_headers,
    )
    user = r.json()
    update_data = {
        "first_name": "test",
        "last_name": "test",
    }
    r = await client.patch(
        f"{configs.API_V1_STR}/users/{user['id']}",
        headers=admin_token_headers,
        json=update_data,
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_delete_user(
    db: Session,
    admin_token_headers: Dict[str, str],
    client: TestClient,
) -> None:
    username, _, id = await create_random_user(db)
    r = await client.delete(
        f"{configs.API_V1_STR}/users/{id}",
        headers=admin_token_headers,
    )
    assert r.status_code == 204

    r = await client.get(
        f"{configs.API_V1_STR}/users{id}",
        headers=admin_token_headers,
        params={
            "username": username,
        },
    )
    assert r.status_code == 404
