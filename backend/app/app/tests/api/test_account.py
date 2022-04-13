from typing import Dict

from fastapi.testclient import TestClient

from app.core.config import configs
from app.tests.utils import random_username


def test_create_delete(
    client: TestClient,
    admin_token_headers: Dict[str, str],
):
    name = random_username()
    r = client.post(
        f"{configs.API_V1_STR}/accounts",
        json={
            "name": name,
            "iaas": "Jelastic",
            "data": {"endpoint": "http://test.com/", "api_key": "test"},
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 201
    js = r.json()
    assert js["name"] == name
    assert js["iaas"]["name"] == "Jelastic"
    assert js["iaas"]["type"] == "PAAS"
    assert js["data"] == {"endpoint": "http://test.com/"}
    r = client.delete(
        f"{configs.API_V1_STR}/accounts/{js['id']}", headers=admin_token_headers
    )
    assert r.status_code == 204


def test_create_wrong_iaas(
    client: TestClient,
    admin_token_headers: Dict[str, str],
):
    name = random_username()
    r = client.post(
        f"{configs.API_V1_STR}/accounts",
        json={
            "name": name,
            "iaas": "asdf",
            "data": {"endpoint": "http://test.com/", "api_key": "test"},
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 422


def test_create_duplicate(
    client: TestClient,
    admin_token_headers: Dict[str, str],
):
    name = random_username()
    r = client.post(
        f"{configs.API_V1_STR}/accounts",
        json={
            "name": name,
            "iaas": "Jelastic",
            "data": {"endpoint": "http://test.com/", "api_key": "test"},
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 201
    acct = r.json()
    r = client.post(
        f"{configs.API_V1_STR}/accounts",
        json={
            "name": name,
            "iaas": "Jelastic",
            "data": {"endpoint": "http://test.com/", "api_key": "test"},
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 409
    js = r.json()
    assert js["detail"] == "Account name already exists"
    r = client.delete(
        f"{configs.API_V1_STR}/accounts/{acct['id']}", headers=admin_token_headers
    )
    assert r.status_code == 204


def test_get_accounts(
    client: TestClient,
    admin_token_headers: Dict[str, str],
):
    r = client.get(f"{configs.API_V1_STR}/accounts", headers=admin_token_headers)
    assert r.status_code == 200
    js = r.json()
    assert js["results"]


def test_filter_accounts(
    client: TestClient,
    admin_token_headers: Dict[str, str],
):
    r = client.get(
        f"{configs.API_V1_STR}/accounts?type=PAAS", headers=admin_token_headers
    )
    assert r.status_code == 200
    js = r.json()
    assert js["results"]
    for account in js["results"]:
        assert account["iaas"]["type"] == "PAAS"


def test_get_id(
    client: TestClient,
    admin_token_headers: Dict[str, str],
):
    # Create one
    name = random_username()
    r = client.post(
        f"{configs.API_V1_STR}/accounts",
        json={
            "name": name,
            "iaas": "Jelastic",
            "data": {"endpoint": "http://test.com/", "api_key": "test"},
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 201
    acct = r.json()
    # Get it
    r = client.get(
        f"{configs.API_V1_STR}/accounts/{acct['id']}", headers=admin_token_headers
    )
    assert r.status_code == 200
    js = r.json()
    assert js["id"] == acct["id"]
    assert js["name"] == name


def test_get_no_exist(
    client: TestClient,
    admin_token_headers: Dict[str, str],
):
    r = client.get(
        f"{configs.API_V1_STR}/accounts/186165135841", headers=admin_token_headers
    )
    assert r.status_code == 404


def test_update(
    client: TestClient,
    admin_token_headers: Dict[str, str],
):
    # Create one
    name = random_username()
    r = client.post(
        f"{configs.API_V1_STR}/accounts",
        json={
            "name": name,
            "iaas": "Jelastic",
            "data": {"endpoint": "http://test.com/", "api_key": "test"},
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 201
    acct = r.json()
    # Update it
    r = client.patch(
        f"{configs.API_V1_STR}/accounts/{acct['id']}",
        json={
            "data": {"endpoint": "http://test.com/", "api_key": "test2"},
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 200
    js = r.json()
    assert js["id"] == acct["id"]
    assert js["name"] == name
    assert js["data"] == {"endpoint": "http://test.com/"}


def test_update_duplicate(
    client: TestClient,
    admin_token_headers: Dict[str, str],
):
    # Create one
    name = random_username()
    name2 = random_username()
    r = client.post(
        f"{configs.API_V1_STR}/accounts",
        json={
            "name": name,
            "iaas": "Jelastic",
            "data": {"endpoint": "http://test.com/", "api_key": "test"},
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 201
    acct = r.json()
    # Create another
    name = random_username()
    r = client.post(
        f"{configs.API_V1_STR}/accounts",
        json={
            "name": name2,
            "iaas": "Jelastic",
            "data": {"endpoint": "http://test.com/", "api_key": "test"},
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 201
    # Update it
    r = client.patch(
        f"{configs.API_V1_STR}/accounts/{acct['id']}",
        json={
            "name": name2,
            "data": {"endpoint": "http://test.com/", "api_key": "test2"},
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 409
    js = r.json()
    assert js["detail"] == "Account name already exists"


def test_no_exist(
    client: TestClient,
    admin_token_headers: Dict[str, str],
):
    r = client.patch(
        f"{configs.API_V1_STR}/accounts/186165135841",
        json={
            "data": {"endpoint": "http://test.com/", "api_key": "test2"},
        },
        headers=admin_token_headers,
    )
    assert r.status_code == 404
