from typing import List, Literal

from pydantic import BaseModel, AnyHttpUrl, validator

from pycloud.base import PaasBase
from pycloud.models import IaasParam, BillingResponse
from pycloud.utils import current_month_date_range
from pycloud import exc


class Endpoint(BaseModel):
    endpoint: AnyHttpUrl
    currency: Literal["USD", "EUR", "GBP"]


endpoints = {
    "Layershift": Endpoint(endpoint="https://app.j.layershift.co.uk/", currency="GBP"),  # type: ignore
    "Eapps": Endpoint(endpoint="https://app.jelastic.eapps.com/", currency="USD"),  # type: ignore
    "Cloudsigma": Endpoint(endpoint="https://app.env2.paas.ruh.cloudsigma.com/", currency="USD"),  # type: ignore
    "Mamazala": Endpoint(endpoint="https://app.pass.mamazala.com/", currency="USD"),  # type: ignore
    "Mirhosting": Endpoint(endpoint="https://app.mircloud.host/", currency="EUR"),  # type: ignore
    "Togglebox": Endpoint(endpoint="https://app.togglebox.cloud/", currency="USD"),  # type: ignore
    "Cloudjiffy": Endpoint(endpoint="https://app.cloudjiffy.com/", currency="USD"),  # type: ignore
    "Massivegrid": Endpoint(endpoint="https://app.paas.massivegrid.com/", currency="USD"),  # type: ignore
}


class Jelastic(PaasBase):
    endpoint: str
    api_key: str

    @validator("endpoint")
    def validate_endpoint(cls, v):
        if v not in endpoints:
            raise ValueError(f"Unknown endpoint: {v}")
        return v

    @staticmethod
    def params() -> List[IaasParam]:
        return [
            # TODO: Change this to names of providers and not urls and currency
            IaasParam(
                key="endpoint",
                label="Endpoint",
                type="choice",
                choices=[k for k in endpoints.keys()],
                readonly=True,
            ),
            IaasParam(key="api_key", label="API Key", type="secret"),
        ]

    def currency(self) -> str:
        return endpoints[self.endpoint].currency

    def __init__(self, **kwargs):  # type: ignore
        super().__init__(**kwargs)
        self._base = endpoints[self.endpoint].endpoint

    async def validate_account(self) -> None:
        data = {
            "appid": "1dd8d191d38fff45e62564fcf67fdcd6",
            "session": self.api_key,
        }
        r = await self._session.get(self.url("/1.0/billing/account/rest/getaccount"), params=data)
        js = r.json()
        if js["result"]:
            # Result should be 0 for success
            raise exc.AuthorizationError(
                "Invalid API key. Please check your API key and try again."
            )

    async def get_current_invoiced(self) -> BillingResponse:
        first_day, last_day = current_month_date_range()
        data = {
            # This is a generic appid for all jelastic apps, use global or "no" environment
            "appid": "1dd8d191d38fff45e62564fcf67fdcd6",
            "session": self.api_key,
            "starttime": first_day.strftime("%Y-%m-%d 00:00:00"),
            "endtime": last_day.strftime("%Y-%m-%d 00:00:00"),
            "period": "MONTH",
        }
        resp = await self._session.get(
            self.url("/1.0/billing/account/rest/getaccountbillinghistorybyperiod"),
            params=data,
            headers=self._headers,
        )
        js = resp.json()
        # Jelastic always returns 200, check internal result non-zero
        if js["result"]:
            if js["result"] == 702:
                raise exc.AuthorizationError(
                    "Invalid API key. Please check your API key and try again."
                )
            else:
                raise exc.UnknownError(f"Unknown error. {js['result']}: {js['error']}")
        total = 0.0
        [total := total + i["cost"] for i in js["array"]]
        data = {
            "appid": "1dd8d191d38fff45e62564fcf67fdcd6",
            "session": self.api_key,
        }
        resp = await self._session.get(
            self.url("/1.0/billing/account/rest/getaccount"),
            params=data,
            headers=self._headers,
        )
        js = resp.json()
        if js["result"]:
            if js["result"] == 702:
                raise exc.AuthorizationError(
                    "Invalid API key. Please check your API key and try again."
                )
            else:
                raise exc.UnknownError(f"Unknown error. {js['result']}: {js['error']}")
        return BillingResponse(
            start_date=first_day,
            end_date=last_day,
            total=total,
            balance=js["balance"],
        )

    async def get_current_usage(self) -> BillingResponse:
        return await self.get_current_invoiced()

    async def get_invoice(self) -> BillingResponse:
        pass
