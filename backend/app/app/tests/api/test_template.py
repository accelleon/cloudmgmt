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
    resp = await client.get(
        f"{configs.API_V1_STR}/accounts",
        headers=admin_token_headers,
    )
    accounts = resp.json()["results"]
    ids = [account["id"] for account in accounts]

    r = await client.post(
        f"{configs.API_V1_STR}/template",
        json={
            "name": random_username(),
            "description": "test",
            "order": ids,
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 201
    js = r.json()
    assert js["name"]
    assert js["description"]
    assert js["order"] == ids

    r = await client.delete(
        f"{configs.API_V1_STR}/template/{js['id']}",
        headers=admin_token_headers,
    )
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_create_duplicate(
    client: TestClient,
    admin_token_headers: Dict[str, str],
):
    resp = await client.get(
        f"{configs.API_V1_STR}/accounts",
        headers=admin_token_headers,
    )
    accounts = resp.json()["results"]
    ids = [account["id"] for account in accounts]

    name = random_username()
    r = await client.post(
        f"{configs.API_V1_STR}/template",
        json={
            "name": name,
            "description": "test",
            "order": ids,
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 201
    js = r.json()
    assert js["name"]
    assert js["description"]
    assert js["order"] == ids

    r = await client.post(
        f"{configs.API_V1_STR}/template",
        json={
            "name": name,
            "description": "test",
            "order": ids,
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_get_templates(
    client: TestClient,
    admin_token_headers: Dict[str, str],
):
    r = await client.get(
        f"{configs.API_V1_STR}/template",
        headers=admin_token_headers,
    )
    assert r.status_code == 200
    js = r.json()
    assert js


@pytest.mark.asyncio
async def test_modify_default(
    client: TestClient,
    admin_token_headers: Dict[str, str],
):
    r = await client.get(
        f"{configs.API_V1_STR}/template",
        headers=admin_token_headers,
    )
    assert r.status_code == 200
    js = r.json()
    assert js
    for template in js:
        if template["name"] == "default":
            r = await client.put(
                f"{configs.API_V1_STR}/template/{template['id']}",
                json={
                    "name": random_username(),
                    "description": "test",
                    "order": [],
                },
                headers=admin_token_headers,
            )
            assert r.status_code == 422
            break


@pytest.mark.asyncio
async def test_delete_default(
    client: TestClient,
    admin_token_headers: Dict[str, str],
):
    r = await client.get(
        f"{configs.API_V1_STR}/template",
        headers=admin_token_headers,
    )
    assert r.status_code == 200
    js = r.json()
    assert js
    for template in js:
        if template["name"] == "default":
            r = await client.delete(
                f"{configs.API_V1_STR}/template/{template['id']}",
                headers=admin_token_headers,
            )
            assert r.status_code == 422
            break


@pytest.mark.asyncio
async def test_modify_invalid_order(
    client: TestClient,
    admin_token_headers: Dict[str, str],
):
    r = await client.get(
        f"{configs.API_V1_STR}/template",
        headers=admin_token_headers,
    )
    assert r.status_code == 200
    js = r.json()
    assert js
    for template in js:
        if template["name"] != "default":
            r = await client.put(
                f"{configs.API_V1_STR}/template/{template['id']}",
                json={
                    "order": [2, 2],
                },
                headers=admin_token_headers,
            )
            assert r.status_code == 422
            break


@pytest.mark.asyncio
async def test_modify_name_exists(
    client: TestClient,
    admin_token_headers: Dict[str, str],
):
    r = await client.get(
        f"{configs.API_V1_STR}/template",
        headers=admin_token_headers,
    )
    assert r.status_code == 200
    js = r.json()
    assert js
    for template in js:
        if template["name"] != "default":
            r = await client.put(
                f"{configs.API_V1_STR}/template/{template['id']}",
                json={
                    "name": "default",
                },
                headers=admin_token_headers,
            )
            assert r.status_code == 409
            break
