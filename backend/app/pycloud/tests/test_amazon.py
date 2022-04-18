import pytest

from pycloud import CloudFactory
from pycloud.utils import current_month_date_range
from pycloud.exc import AuthorizationError


def test_billing() -> None:
    client = CloudFactory.get_client(
        "Amazon",
        {
            "access_key": "asdf",
            "secret_key": "asdf",
        },
    )
    bill = client.get_current_billing()
    assert bill.start_date == current_month_date_range()[0]
    assert bill.end_date == current_month_date_range()[1]
    assert bill.total > 0
    assert bill.balance is None


def test_wrong_cred() -> None:
    client = CloudFactory.get_client(
        "Amazon",
        {
            "access_key": "asdf",
            "secret_key": "asdf",
        },
    )

    with pytest.raises(AuthorizationError):
        client.get_current_billing()
