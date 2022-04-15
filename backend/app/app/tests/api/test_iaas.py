from typing import Dict

from fastapi.testclient import TestClient

from pycloud import CloudFactory
from app.core.config import configs
from app.model.iaas import IaasType


def test_iaas_get_all(
    client: TestClient,
    admin_token_headers: Dict[str, str],
) -> None:
    providers = CloudFactory.get_providers()
    r = client.get(f"{configs.API_V1_STR}/providers", headers=admin_token_headers)
    assert r.status_code == 200
    js = r.json()
    assert len(js["results"]) == len(providers)
    iaas = {p.name: p for p in providers}
    for i in js["results"]:
        assert i["name"]
        assert i["type"] == iaas[i["name"]].type.value
        assert i["params"] == iaas[i["name"]].params


def test_iaas_get_all_filter(
    client: TestClient,
    admin_token_headers: Dict[str, str],
) -> None:
    providers = CloudFactory.get_providers()
    r = client.get(
        f"{configs.API_V1_STR}/providers?type=PAAS", headers=admin_token_headers
    )
    assert r.status_code == 200
    js = r.json()
    names = [x["name"] for x in js["results"]]
    assert len(names) == len([p for p in providers if p.type == IaasType.PAAS])
    for provider in providers:
        if provider.type.value == "PAAS":
            assert provider.name in names
        else:
            assert provider.name not in names


def test_get_one(
    client: TestClient,
    admin_token_headers: Dict[str, str],
) -> None:
    r = client.get(f"{configs.API_V1_STR}/providers", headers=admin_token_headers)
    js = r.json()
    r = client.get(f"{configs.API_V1_STR}/providers/{js['results'][0]['id']}", headers=admin_token_headers)
    assert r.status_code == 200
    js = r.json()
    assert "name" in js
    assert "type" in js
    assert "params" in js
    assert "accounts" in js
    # Check the relationship
    assert js["accounts"]
    assert "id" in js["accounts"][0]
    assert "name" in js["accounts"][0]


def test_iaas_get_one_not_found(
    client: TestClient,
    admin_token_headers: Dict[str, str],
) -> None:
    r = client.get(
        f"{configs.API_V1_STR}/providers/1561681355", headers=admin_token_headers
    )
    assert r.status_code == 404
    js = r.json()
    assert js["detail"] == "Provider not found"
