import pytest

from pycloud import CloudFactory
from pycloud.utils import current_month_date_range
from pycloud.exc import AuthorizationError


@pytest.mark.asyncio
async def test_billing() -> None:
    client = CloudFactory.get_client(
        "Amazon",
        {
            "access_key": "asdf",
            "secret_key": "asdf",
        },
    )
    bill = await client.get_billing("2022-04")
    assert bill.start_date == current_month_date_range()[0]
    assert bill.end_date == current_month_date_range()[1]
    assert bill.total > 0
    assert bill.balance is None


@pytest.mark.asyncio
async def test_wrong_cred() -> None:
    client = CloudFactory.get_client(
        "Amazon",
        {
            "access_key": "asdf",
            "secret_key": "asdf",
        },
    )

    with pytest.raises(AuthorizationError):
        await client.get_billing("2022-04")


@pytest.mark.asyncio
async def test_get_instances() -> None:
    client = CloudFactory.get_client(
        "Amazon",
        {
            "access_key": "",
            "secret_key": "",
        },
    )
    instances = await client.get_instances()
    assert instances
