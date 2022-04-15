from typing import TYPE_CHECKING, List, Dict, Literal
from datetime import datetime

from pydantic import BaseModel, HttpUrl, SecretStr
from dateutil.relativedelta import relativedelta

from pycloud.base import PaasBase
from pycloud.models import IaasParam

if TYPE_CHECKING:
    from app.model.billing import CreateBillingPeriod


class Endpoint(BaseModel):
    endpoint: HttpUrl
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
    api_key: SecretStr
    _endpoint = None

    @staticmethod
    def params() -> List[IaasParam]:

        return [
            # TODO: Change this to names of providers and not urls and currency
            IaasParam(
                key="endpoint",
                label="Endpoint",
                type="choice",
                choices=[k for k in endpoints.keys()],
            ),
            IaasParam(key="api_key", label="API Key", type="secret"),
        ]

    @classmethod
    def check_params(cls, data: Dict[str, str]) -> None:
        cls(**data)

    def __init__(self, **kwargs):  # type: ignore
        super().__init__(**kwargs)
        self._endpoint = endpoints[self.endpoint]

    async def get_current_billing(self) -> "CreateBillingPeriod":
        # Some date magic
        # Just first of this month, Start is inclusive
        first_day = datetime.today().replace(day=1)
        # This increments month by 1 and sets day to 1, End is exclusive
        last_day = datetime.today() + relativedelta(months=1, day=1)
        data = {
            # This is a generic appid for all jelastic apps, use global or "no" environment
            "appid": "1dd8d191d38fff45e62564fcf67fdcd6",
            "session": self.api_key,
            "starttime": first_day.strftime("%Y-%m-%d 00:00:00"),
            "endtime": last_day.strftime("%Y-%m-%d 00:00:00"),
            "period": "MONTH",
        }
        resp = self._session.get(
            "/1.0/billing/account/rest/getaccountbillinghistorybyperiod",
            json=data,
        )
        js = resp.json()
        total = 0.0
        [total := total + i["cost"] for i in js["array"]]
        data = {
            "appid": "1dd8d191d38fff45e62564fcf67fdcd6",
            "session": self.api_key,
        }
        resp = self._session.get(
            "/1.0/billing/account/rest/getaccount",
            json=data,
        )
        js = resp.json()
        return CreateBillingPeriod(
            account_id=self._id,
            start_date=first_day,
            end_date=last_day,
            total=total,
            balance=js["balance"],
        )
