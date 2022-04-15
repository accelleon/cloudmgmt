from typing import List
from datetime import datetime

import requests

from pycloud.base import IaasBase
from pycloud.models import BillingResponse, IaasParam


class Rackspace(IaasBase):
    token: str

    @staticmethod
    def params() -> List[IaasParam]:
        return [
            IaasParam(key="token", label="Token", type="secret"),
        ]

    def __init__(self, **data):
        super().__init__(**data)
        self._client = requests.Session()
        self._client.headers.update({"Authorization": f"Bearer {self.token}"})

    def get_current_billing(self) -> BillingResponse:
        """
        Returns the current billing for the current month.
        """
        return BillingResponse(
            total=0.0,
            balance=0.0,
            start_date=datetime.now(),
            end_date=datetime.now(),
        )
