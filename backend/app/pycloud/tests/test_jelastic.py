import pytest

from pycloud import CloudFactory
from pycloud.utils import current_month_date_range
from pycloud.exc import AuthorizationError


def test_billing() -> None:
    client = CloudFactory.get_client(
        "Jelastic",
        {
            "endpoint": "Layershift",
            "api_key": "asdf",
        },
    )
    bill = client.get_current_billing()
    assert bill.start_date == current_month_date_range()[0]
    assert bill.end_date == current_month_date_range()[1]
    assert bill.total > 0
    assert bill.balance is not None
    assert client.currency() == "GBP"


def test_wrong_cred() -> None:
    client = CloudFactory.get_client(
        "Jelastic",
        {
            "endpoint": "Layershift",
            "api_key": "asdfeaefae",
        },
    )

    with pytest.raises(AuthorizationError):
        client.get_current_billing()


def test_currency() -> None:
    client = CloudFactory.get_client(
        "Jelastic",
        {
            "endpoint": "Eapps",
            "api_key": "asdf",
        },
    )
    assert client.currency() == "USD"
    client = CloudFactory.get_client(
        "Jelastic",
        {
            "endpoint": "Layershift",
            "api_key": "asdf",
        },
    )
    assert client.currency() == "GBP"
