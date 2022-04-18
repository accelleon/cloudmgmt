import pytest

from pycloud import CloudFactory
from pycloud.utils import current_month_date_range
from pycloud.exc import AuthorizationError


def test_billing() -> None:
    client = CloudFactory.get_client(
        "Heroku",
        {
            "api_key": "adsf",
        },
    )

    start, end = current_month_date_range()

    bill = client.get_current_billing()
    assert bill.start_date == start
    assert bill.end_date == end
    assert bill.total > 0
    assert bill.balance is None


def test_wrong_cred() -> None:
    client = CloudFactory.get_client(
        "Heroku",
        {
            "api_key": "asdfeaefae",
        },
    )

    with pytest.raises(AuthorizationError):
        client.get_current_billing()
