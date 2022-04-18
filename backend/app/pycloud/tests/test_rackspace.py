import pytest

from pycloud import CloudFactory
from pycloud.exc import AuthorizationError, UnknownError


def test_billing() -> None:
    client = CloudFactory.get_client(
        "Rackspace",
        {
            "username": "asdf",
            "api_key": "asdf",
            "ran": "0000",
        },
    )

    bill = client.get_current_billing()
    assert bill.start_date
    assert bill.end_date
    assert bill.total > 0
    assert bill.balance is None


def test_wrong_cred() -> None:
    client = CloudFactory.get_client(
        "Rackspace",
        {
            "username": "asdf",
            "api_key": "afeageae",
            "ran": "000",
        },
    )

    with pytest.raises(AuthorizationError):
        client.get_current_billing()


def test_wrong_ran() -> None:
    client = CloudFactory.get_client(
        "Rackspace",
        {
            "username": "dexterneer",
            "api_key": "asdf",
            "ran": "0000",
        },
    )

    with pytest.raises(UnknownError):
        client.get_current_billing()
