from typing import Any, List
from datetime import datetime

import ovh

from pycloud.base import IaasBase
from pycloud.models import BillingResponse, IaasParam
from pycloud.utils import current_month_date_range
from pycloud import exc


class OVHCloud(IaasBase):
    endpoint: str
    app_key: str
    app_secret: str
    consumer_key: str

    _client: Any

    @staticmethod
    def params() -> List[IaasParam]:
        return [
            IaasParam(
                key="endpoint",
                label="Endpoint",
                type="choice",
                choices=["ovh-eu", "ovh-ca", "ovh-us"],
            ),
            IaasParam(key="app_key", label="App Key", type="string"),
            IaasParam(key="app_secret", label="App Secret", type="secret"),
            IaasParam(key="consumer_key", label="Consumer Key", type="string"),
        ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._client = ovh.Client(
            endpoint=self.endpoint,
            application_key=self.app_key,
            application_secret=self.app_secret,
            consumer_key=self.consumer_key,
        )

    def get_current_billing(self) -> BillingResponse:
        """
        Returns the current billing for the current month.
        """
        start, end = current_month_date_range()

        try:
            bills = self._client.get("/me/bill")
        except ovh.exceptions.InvalidCredential:
            raise exc.AuthorizationError("Invalid consumer key")
        except ovh.exceptions.InvalidKey:
            raise exc.AuthorizationError("Invalid application key or secret")
        except Exception as e:
            raise exc.UnknownError(e)

        prevBilling = None
        billDate = None

        for billid in bills:
            bill = self._client.get(f"/me/bill/{billid}")
            ptime = datetime.fromisoformat(bill["date"])
            if billDate is None or ptime > billDate:
                billDate = ptime
                prevBilling = bill

        # TODO: Properly handle the case where there are no bills
        if prevBilling is None:
            raise Exception("No bill found")

        return BillingResponse(
            total=prevBilling["priceWithTax"]["value"],
            balance=None,
            start_date=start,
            end_date=end,
        )
