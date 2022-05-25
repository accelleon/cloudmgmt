from typing import Dict

import pytest
from httpx import AsyncClient as TestClient

from app.core.config import configs
from app.tests.utils import random_username


@pytest.mark.asyncio
async def test_create_delete(
    client: TestClient,
    admin_token_headers: Dict[str, str],
):
    name = random_username()
    r = await client.post(
        f"{configs.API_V1_STR}/groups",
        json={
            "name": name,
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 201
    js = r.json()
    assert js["name"] == name
    assert js["accounts"] == []
    r = await client.delete(
        f"{configs.API_V1_STR}/groups/{js['id']}", headers=admin_token_headers
    )
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_create_duplicate(
    client: TestClient,
    admin_token_headers: Dict[str, str],
):
    name = random_username()
    r = await client.post(
        f"{configs.API_V1_STR}/groups",
        json={
            "name": name,
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 201
    r = await client.post(
        f"{configs.API_V1_STR}/groups",
        json={
            "name": name,
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_get_group(
    client: TestClient,
    admin_token_headers: Dict[str, str],
):
    name = random_username()
    r = await client.post(
        f"{configs.API_V1_STR}/groups",
        json={
            "name": name,
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 201
    js = r.json()
    r = await client.get(
        f"{configs.API_V1_STR}/groups/{js['id']}", headers=admin_token_headers
    )
    assert r.status_code == 200
    js = r.json()
    assert js["name"] == name
    r = await client.delete(
        f"{configs.API_V1_STR}/groups/{js['id']}", headers=admin_token_headers
    )
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_get_group_not_found(
    client: TestClient,
    admin_token_headers: Dict[str, str],
):
    r = await client.get(f"{configs.API_V1_STR}/groups/1", headers=admin_token_headers)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_get_groups(
    client: TestClient,
    admin_token_headers: Dict[str, str],
):
    r = await client.get(f"{configs.API_V1_STR}/groups", headers=admin_token_headers)
    assert r.status_code == 200
    js = r.json()
    assert not js["results"]


@pytest.mark.asyncio
async def test_get_groups_with_accounts(
    client: TestClient,
    admin_token_headers: Dict[str, str],
):
    r = await client.post(
        f"{configs.API_V1_STR}/groups",
        json={
            "name": random_username(),
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 201
    group = r.json()
    name = random_username()
    r = await client.post(
        f"{configs.API_V1_STR}/accounts",
        json={
            "name": name,
            "iaas": "Heroku",
            "data": {"api_key": "test"},
            "group": group["name"],
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 201
    account_id = r.json()["id"]
    r = await client.get(
        f"{configs.API_V1_STR}/groups/{group['id']}", headers=admin_token_headers
    )
    js = r.json()
    assert js["accounts"]
    assert js["accounts"][0]["id"] == account_id
