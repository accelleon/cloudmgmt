from typing import List, Dict, Any

from pycloud.base import IaasBase
from pycloud.models import BillingResponse, IaasParam
from pycloud import exc


class Rackspace(IaasBase):
    username: str
    api_key: str
    ran: str

    _services: Dict[str, Any]

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

    async def authenticate(self) -> None:
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

        self._services = {service["name"]: service for service in js["access"]["serviceCatalog"]}

    async def validate_account(self) -> None:
        await self.authenticate()

    async def get_current_invoiced(self) -> BillingResponse:
        """
        Returns the current billing for the current month.
        """
        await self.authenticate()

        resp = await self._session.get(
            self.url("/v2/accounts/{ran}/estimated_charges".format(ran=self.ran)),
            headers=self._headers,
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

    async def get_instance_count(self) -> int:
        await self.authenticate()
        endpoints = self._services["cloudServersOpenStack"]["endpoints"]
        count = 0
        for endpoint in endpoints:
            resp = await self._session.get(
                f"{endpoint['publicURL']}/servers/detail", headers=self._headers
            )
            if resp.status_code != 200:
                raise exc.UnknownError(f"Failed to get Rackspace servers: {resp.text}")
            js = resp.json()
            count += len(js["servers"])
        return count
