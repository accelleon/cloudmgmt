from typing import List

from pycloud.base import SIPBase
from pycloud.models import IaasParam, BillingResponse
from pycloud.utils import current_month_date_range
from pycloud import exc


class Nexmo(SIPBase):
    api_key: str
    api_secret: str

    @staticmethod
    def params() -> List[IaasParam]:
        return [
            IaasParam(key="api_key", label="API Key", type="secret"),
            IaasParam(key="api_secret", label="API Secret", type="secret"),
        ]

    def currency(self) -> str:
        return "EUR"

    def __init__(self, **kwargs):  # type: ignore
        super().__init__(**kwargs)
        self._base = "https://rest.nexmo.com/"

    async def validate_account(self) -> None:
        r = await self._session.get(
            self.url("/account/get-balance"),
            params={"api_key": self.api_key, "api_secret": self.api_secret},
        )
        if r.status_code != 200:
            if r.status_code == 401:
                raise exc.AuthorizationError("Invalid API key or secret")
            else:
                raise exc.UnknownError(f"Unexpected error occurred: {r.text}")

    async def get_current_invoiced(self) -> BillingResponse:
        start, end = current_month_date_range()
        r = await self._session.get(
            self.url("/account/get-balance"),
            params={"api_key": self.api_key, "api_secret": self.api_secret},
        )
        if r.status_code != 200:
            if r.status_code == 401:
                raise exc.AuthorizationError("Invalid API key or secret")
            else:
                raise exc.UnknownError(f"Unexpected error occurred: {r.text}")
        js = r.json()
        return BillingResponse(
            start_date=start, end_date=end, total=0.0, balance=js["value"]
        )

    async def get_current_usage(self) -> BillingResponse:
        pass

    async def get_invoice(self) -> BillingResponse:
        pass
