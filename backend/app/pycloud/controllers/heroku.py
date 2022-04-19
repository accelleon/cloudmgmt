from typing import List

from pycloud.base import PaasBase
from pycloud.models import BillingResponse, IaasParam
from pycloud.utils import current_month_date_range
from pycloud import exc


class Heroku(PaasBase):
    api_key: str

    @staticmethod
    def params() -> List[IaasParam]:
        return [
            IaasParam(key="api_key", label="API Key", type="secret"),
        ]

    def __init__(self, **data):
        super().__init__(**data)
        self._base = "https://api.heroku.com/"  # type: ignore
        self._headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/vnd.heroku+json; version=3",
            }
        )

    async def get_current_billing(self) -> BillingResponse:
        """
        Returns the current billing for the current month.
        """
        resp = await self._session.get(
            self.url("/account/invoices"),
            headers=self._headers,
        )

        if resp.status_code != 200:
            if resp.status_code == 401:
                raise exc.AuthorizationError(
                    "Invalid API key. Please check your Heroku API key."
                )
            else:
                raise exc.UnknownError(
                    "Failed to get Heroku billing: {}".format(resp.text)
                )

        start, end = current_month_date_range()
        month = start.strftime("%Y-%m")
        js = resp.json()
        for invoice in js:
            if month in invoice["period_start"]:
                return BillingResponse(
                    total=invoice["total"],
                    balance=None,
                    start_date=start,
                    end_date=end,
                )

        raise Exception("No invoice found for the current month")
