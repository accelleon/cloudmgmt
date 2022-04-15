from pycloud import CloudFactory
from pycloud.utils import current_month_date_range


def test_billing() -> None:
    client = CloudFactory.get_client(
        "Jelastic",
        {
            "endpoint": "Layershift",
            "api_key": "**********",
        }
    )
    bill = client.get_current_billing()
    assert bill.start_date == current_month_date_range()[0]
    assert bill.end_date == current_month_date_range()[1]
    assert bill.total > 0
    assert bill.balance > 0
