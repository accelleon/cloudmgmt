from typing import Dict

from fastapi.testclient import TestClient

from app.core.config import configs


def test_get_billing(
    client: TestClient,
    user_token_headers: Dict[str, str],
):
    r = client.get(
        f"{configs.API_V1_STR}/billing",
        headers=user_token_headers,
    )
    assert r.status_code == 200
    js = r.json()
    assert "results" in js
    assert js["results"]
    assert "total" in js["results"][0]
    assert "account" in js["results"][0]
    assert "balance" in js["results"][0]
    assert "start_date" in js["results"][0]
    assert "end_date" in js["results"][0]
    assert "id" in js["results"][0]
    assert "account_id" in js["results"][0]
    assert "iaas_id" in js["results"][0]["account"]
