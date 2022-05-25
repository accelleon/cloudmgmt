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
    r = await client.post(
        f"{configs.API_V1_STR}/accounts",
        json={
            "name": name,
            "iaas": "Heroku",
            "data": {"api_key": "test"},
            "group": name,
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 201
    js = r.json()
    assert js["name"] == name
    assert js["iaas"]["name"] == "Heroku"
    assert js["iaas"]["type"] == "PAAS"
    assert js["currency"] == "USD"
    assert "api_key" not in js["data"]
    r = await client.delete(
        f"{configs.API_V1_STR}/accounts/{js['id']}", headers=admin_token_headers
    )
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_create_wrong_iaas(
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
    r = await client.post(
        f"{configs.API_V1_STR}/accounts",
        json={
            "name": name,
            "iaas": "asdf",
            "data": {"endpoint": "Layershift", "api_key": "test"},
            "group": name,
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_create_no_group(
    client: TestClient,
    admin_token_headers: Dict[str, str],
):
    name = random_username()
    r = await client.post(
        f"{configs.API_V1_STR}/accounts",
        json={
            "name": name,
            "iaas": "Heroku",
            "data": {"api_key": "test"},
            "group": name,
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 422


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
    r = await client.post(
        f"{configs.API_V1_STR}/accounts",
        json={
            "name": name,
            "iaas": "Heroku",
            "data": {"api_key": "test"},
            "group": name,
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 201
    acct = r.json()
    r = await client.post(
        f"{configs.API_V1_STR}/accounts",
        json={
            "name": name,
            "iaas": "Heroku",
            "data": {"api_key": "test"},
            "group": name,
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 409
    js = r.json()
    assert js["detail"] == "Account name already exists"
    r = await client.delete(
        f"{configs.API_V1_STR}/accounts/{acct['id']}", headers=admin_token_headers
    )
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_get_accounts(
    client: TestClient,
    admin_token_headers: Dict[str, str],
):
    r = await client.get(f"{configs.API_V1_STR}/accounts", headers=admin_token_headers)
    assert r.status_code == 200
    js = r.json()
    assert js["results"]


@pytest.mark.asyncio
async def test_filter_accounts(
    client: TestClient,
    admin_token_headers: Dict[str, str],
):
    r = await client.get(
        f"{configs.API_V1_STR}/accounts?type=PAAS", headers=admin_token_headers
    )
    assert r.status_code == 200
    js = r.json()
    assert js["results"]
    for account in js["results"]:
        assert account["iaas"]["type"] == "PAAS"


@pytest.mark.asyncio
async def test_get_id(
    client: TestClient,
    admin_token_headers: Dict[str, str],
):
    # Create one
    name = random_username()
    r = await client.post(
        f"{configs.API_V1_STR}/groups",
        json={
            "name": name,
        },
        headers=admin_token_headers,
    )
    r = await client.post(
        f"{configs.API_V1_STR}/accounts",
        json={
            "name": name,
            "iaas": "Heroku",
            "data": {"api_key": "test"},
            "group": name,
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 201
    acct = r.json()
    # Get it
    r = await client.get(
        f"{configs.API_V1_STR}/accounts/{acct['id']}", headers=admin_token_headers
    )
    assert r.status_code == 200
    js = r.json()
    assert js["id"] == acct["id"]
    assert js["name"] == name


@pytest.mark.asyncio
async def test_get_no_exist(
    client: TestClient,
    admin_token_headers: Dict[str, str],
):
    r = await client.get(
        f"{configs.API_V1_STR}/accounts/1861651", headers=admin_token_headers
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_update(
    client: TestClient,
    admin_token_headers: Dict[str, str],
):
    # Create one
    name = random_username()
    r = await client.post(
        f"{configs.API_V1_STR}/groups",
        json={
            "name": name,
        },
        headers=admin_token_headers,
    )
    r = await client.post(
        f"{configs.API_V1_STR}/accounts",
        json={
            "name": name,
            "iaas": "Jelastic",
            "data": {"endpoint": "Layershift", "api_key": "test"},
            "group": name,
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 201
    acct = r.json()
    # Update it
    r = await client.patch(
        f"{configs.API_V1_STR}/accounts/{acct['id']}",
        json={
            "data": {"endpoint": "Layershift", "api_key": "test2"},
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 200
    js = r.json()
    assert js["id"] == acct["id"]
    assert js["name"] == name
    assert js["data"] == {"endpoint": "Layershift"}


@pytest.mark.asyncio
async def test_update_duplicate(
    client: TestClient,
    admin_token_headers: Dict[str, str],
):
    # Create one
    name = random_username()
    name2 = random_username()
    r = await client.post(
        f"{configs.API_V1_STR}/groups",
        json={
            "name": name,
        },
        headers=admin_token_headers,
    )
    r = await client.post(
        f"{configs.API_V1_STR}/accounts",
        json={
            "name": name,
            "iaas": "Heroku",
            "data": {"api_key": "test"},
            "group": name,
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 201
    acct = r.json()
    print(acct)
    # Create another
    r = await client.post(
        f"{configs.API_V1_STR}/accounts",
        json={
            "name": name2,
            "iaas": "Heroku",
            "data": {"api_key": "test"},
            "group": name,
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 201
    # Update it
    r = await client.patch(
        f"{configs.API_V1_STR}/accounts/{acct['id']}",
        json={
            "name": name2,
            "data": {"api_key": "test2"},
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 409
    js = r.json()
    assert js["detail"] == "Account name already exists"


@pytest.mark.asyncio
async def test_no_exist(
    client: TestClient,
    admin_token_headers: Dict[str, str],
):
    r = await client.patch(
        f"{configs.API_V1_STR}/accounts/186165",
        json={
            "data": {"endpoint": "Layershift", "api_key": "test2"},
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 404
