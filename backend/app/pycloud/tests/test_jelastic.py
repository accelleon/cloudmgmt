from pycloud import CloudFactory
from pycloud.utils import current_month_date_range


def test_billing() -> None:
    client = CloudFactory.get_client(
        "Jelastic",
        {
            "endpoint": "Layershift",
            "api_key": "**********",
        },
    )
    bill = client.get_current_billing()
    assert bill.start_date == current_month_date_range()[0]
    assert bill.end_date == current_month_date_range()[1]
    assert bill.total > 0
    assert bill.balance is not None
    assert client.currency() == "GBP"


def test_currency() -> None:
    client = CloudFactory.get_client(
        "Jelastic",
        {
            "endpoint": "Eapps",
            "api_key": "**********",
        },
    )
    assert client.currency() == "USD"
    client = CloudFactory.get_client(
        "Jelastic",
        {
            "endpoint": "Layershift",
            "api_key": "**********",
        },
    )
    assert client.currency() == "GBP"
