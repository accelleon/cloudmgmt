from typing import List
from datetime import datetime

import boto3
from pydantic import SecretStr

from pycloud.base import IaasBase
from pycloud.models import BillingResponse, IaasParam


class Amazon(IaasBase):
    access_key: str
    secret_key: SecretStr

    @staticmethod
    def params() -> List[IaasParam]:
        return [
            IaasParam(key="access_key", label="Access Key", type="string"),
            IaasParam(key="secret_key", label="Secret Key", type="secret"),
        ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._client = boto3.client(
            "ec2",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name="eu-west-1",
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
