from typing import Dict

import pytest
from httpx import AsyncClient as TestClient
from sqlalchemy.ext.asyncio import AsyncSession as Session

from app.core.config import configs
from app import database
from app.model import CreateAccount, CreateBillingPeriod
from app.tests.utils import random_username

from pycloud.utils import current_month_date_range


@pytest.mark.asyncio
async def test_get_billing(
    db: Session,
    client: TestClient,
    user_token_headers: Dict[str, str],
):
    iaas = await database.iaas.get_by_name(db, name="Jelastic")
    assert iaas
    data = CreateAccount(
        name=random_username(),
        iaas="Jelastic",
        data={"endpoint": "Layershift", "api_key": "test"},
    )
    acct = await database.account.create(db, obj_in=data)

    (start, end) = current_month_date_range()

    obj_in = CreateBillingPeriod(
        account_id=acct.id,
        total=100,
        balance=50,
        start_date=start,
        end_date=end,
    )
    await database.billing.create(db, obj_in=obj_in)

    r = await client.get(
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
