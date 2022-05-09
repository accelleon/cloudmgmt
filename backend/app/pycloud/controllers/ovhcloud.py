from typing import Any, List
from datetime import datetime

import ovh
from asgiref.sync import sync_to_async

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

    async def validate_account(self) -> None:
        def _validate_account():
            try:
                self._client.get("/me")
            except ovh.exceptions.InvalidCredential:
                raise exc.AuthorizationError("Invalid consumer key")
            except ovh.exceptions.InvalidKey:
                raise exc.AuthorizationError("Invalid application key or secret")
            except Exception as e:
                raise exc.UnknownError(e)

        await sync_to_async(_validate_account)()

    async def get_current_invoiced(self) -> BillingResponse:
        start, end = current_month_date_range()

        try:
            # TODO: Wrap in async call
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

    async def get_current_usage(self) -> BillingResponse:
        start, end = current_month_date_range()

        try:
            usage = self._client.get("me/consumption/usage/forecast")
        except ovh.exceptions.InvalidCredential:
            raise exc.AuthorizationError("Invalid consumer key")
        except ovh.exceptions.InvalidKey:
            raise exc.AuthorizationError("Invalid application key or secret")
        except Exception as e:
            raise exc.UnknownError(e)

        try:
            total = usage[0]["price"]["value"]
        except (TypeError, IndexError):
            total = 0

        return BillingResponse(
            total=total,
            balance=None,
            start_date=start,
            end_date=end,
        )

    async def get_invoice(self) -> BillingResponse:
        pass
