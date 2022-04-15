from typing import List
from datetime import datetime

from pycloud.base import IaasBase
from pycloud.models import IaasParam, BillingResponse
from pycloud.utils import current_month_date_range


class DigitalOcean(IaasBase):
    token: str

    @staticmethod
    def params() -> List[IaasParam]:
        return [
            IaasParam(key="token", label="Token", type="secret"),
        ]

    def __init__(self, **data):
        super().__init__(**data)
        self._session.headers.update({"Authorization": f"Bearer {self.token}"})
        self._base = "https://api.digitalocean.com/v2"  # type: ignore

    def get_current_billing(self) -> BillingResponse:
        """
        Returns the current billing for the current month.
        """
        r = self._session.get(
            self.url("/customers/my/balance"),
        )
        js = r.json()
        start, end = current_month_date_range()
        return BillingResponse(
            total=js['month_to_date_usage'],
            balance=None,
            start_date=start,
            end_date=end,
        )
