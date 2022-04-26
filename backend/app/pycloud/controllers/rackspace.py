from typing import List

from pycloud.base import IaasBase
from pycloud.models import BillingResponse, IaasParam
from pycloud import exc


class Rackspace(IaasBase):
    username: str
    api_key: str
    ran: str

    @staticmethod
    def params() -> List[IaasParam]:
        return [
            IaasParam(key="username", label="Username", type="string"),
            IaasParam(key="ran", label="Account Number", type="string"),
            IaasParam(key="api_key", label="API Key", type="secret"),
        ]

    def __init__(self, **data):
        super().__init__(**data)
        self._base = "https://billing.api.rackspacecloud.com/"  # type: ignore

    async def get_current_invoiced(self) -> BillingResponse:
        """
        Returns the current billing for the current month.
        """
        resp = await self._session.post(
            "https://identity.api.rackspacecloud.com/v2.0/tokens",
            headers=self._headers,
            json={
                "auth": {
                    "RAX-KSKEY:apiKeyCredentials": {
                        "username": self.username,
                        "apiKey": self.api_key,
                    },
                },
            },
        )
        if resp.status_code != 200:
            if resp.status_code == 401:
                raise exc.AuthorizationError(
                    "Invalid API key. Please check your Rackspace API key."
                )
            else:
                raise exc.UnknownError(
                    "Failed to get Rackspace billing: {}".format(resp.text)
                )
        js = resp.json()
        token = js["access"]["token"]["id"]
        self._headers.update({"X-Auth-Token": token})

        resp = await self._session.get(
            self.url("/v2/accounts/{ran}/estimated_charges".format(ran=self.ran)),
            headers=self._headers,
        )
        if not resp.status_code != 200:
            if resp.status_code == 401:
                raise exc.AuthorizationError(
                    "Invalid API key. Please check your Rackspace API key."
                )
            else:
                raise exc.UnknownError(
                    "Failed to get Rackspace billing: {}".format(resp.text)
                )
        js = resp.json()
        return BillingResponse(
            total=js["estimatedCharges"]["chargeTotal"],
            balance=None,
            start_date=js["estimatedCharges"]["currentBillingPeriodStartDate"],
            end_date=js["estimatedCharges"]["currentBillingPeriodEndDate"],
        )

    async def get_current_usage(self) -> BillingResponse:
        return await self.get_current_invoiced()

    async def get_invoice(self) -> BillingResponse:
        pass
