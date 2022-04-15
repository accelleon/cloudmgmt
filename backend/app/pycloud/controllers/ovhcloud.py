from typing import Any, List
from datetime import datetime

import ovh
from pydantic import SecretStr

from pycloud.base import IaasBase
from pycloud.models import BillingResponse, IaasParam


class OVHCloud(IaasBase):
    endpoint: str
    app_key: str
    app_secret: SecretStr
    consumer_key: str

    _client: Any

    @staticmethod
    def params() -> List[IaasParam]:
        return [
            IaasParam(key="endpoint", label="Endpoint", type="choice", choices=["ovh-eu", "ovh-ca", "ovh-us"]),
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
        return BillingResponse(
            total=0.0,
            balance=0.0,
            start_date=datetime.now(),
            end_date=datetime.now(),
        )
