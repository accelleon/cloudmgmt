from typing import List

from pycloud.base import IaasBase
from pycloud.models import IaasParam, BillingResponse
from pycloud.utils import current_month_date_range
from pycloud import exc


class DigitalOcean(IaasBase):
    api_key: str

    @staticmethod
    def params() -> List[IaasParam]:
        return [
            IaasParam(key="api_key", label="Token", type="secret"),
        ]

    def __init__(self, **data):
        super().__init__(**data)
        self._headers.update({"Authorization": f"Bearer {self.api_key}"})
        self._base = "https://api.digitalocean.com/"  # type: ignore

    async def get_current_billing(self) -> BillingResponse:
        """
        Returns the current billing for the current month.
        """
        r = await self._session.get(
            self.url("/v2/customers/my/balance"),
            headers=self._headers,
        )
        if r.status_code == 401:
            raise exc.AuthorizationError(
                "Invalid API key. Please check your DigitalOcean API key."
            )
        if r.status_code != 200:
            raise exc.UnknownError(
                "Failed to get DigitalOcean billing: {}".format(r.text)
            )
        js = r.json()
        start, end = current_month_date_range()
        return BillingResponse(
            total=js["month_to_date_usage"],
            balance=None,
            start_date=start,
            end_date=end,
        )
