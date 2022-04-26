from typing import List, Literal, Tuple

from pycloud.base import IaasBase
from pycloud.models import BillingResponse, IaasParam
from pycloud import exc
from pycloud.utils import current_month_date_range


class CloudSigma(IaasBase):
    username: str
    password: str
    endpoint: Literal[
        "crk",
        "dub",
        "fra",
        "gva",
        "hnl",
        "lla",
        "mel",
        "mnl",
        "mnl2",
        "per",
        "ruh",
        "sjc",
        "tyo",
        "wdc",
        "zrh",
    ]

    _auth: Tuple[str, str]

    @staticmethod
    def params() -> List[IaasParam]:
        return [
            IaasParam(key="username", label="Username", type="string"),
            IaasParam(key="password", label="Password", type="secret"),
            IaasParam(
                key="endpoint",
                label="Endpoint",
                type="choice",
                choices=[
                    "crk",
                    "dub",
                    "fra",
                    "gva",
                    "hnl",
                    "lla",
                    "mel",
                    "mnl",
                    "mnl2",
                    "per",
                    "ruh",
                    "sjc",
                    "tyo",
                    "wdc",
                    "zrh",
                ],
                readonly=True,
            ),
        ]

    def __init__(self, **data):
        super().__init__(**data)
        self._base = f"https://{self.endpoint}.cloudsigma.com/"
        self._auth = (self.username, self.password)

    async def get_current_invoiced(self) -> BillingResponse:
        start, end = current_month_date_range()
        # First retrieve our account balance
        x = await self._session.get(self.url("/balance"), auth=self._auth)
        if x.status_code != 200:
            raise Exception(f"failed to retreive balance {x}")
        js = x.json()
        balance = round(float(js["balance"]), 2)

        # Query parameters, filter by what we want
        # our first request we want nothing returned, we simply want the total count that our query returns
        params = {
            "time__gt": start.strftime("%Y-%m-%d"),
            "time__lt": end.strftime("%Y-%m-%d"),
            "limit": 0,
        }

        # Do the thing
        x = await self._session.get(self.url("/ledger"), auth=self._auth, params=params)
        if x.status_code != 200:
            raise Exception(f"failed to retreive monthly usage {x}")
        js = x.json()

        # Set the limit for our next request, grab everything
        params["limit"] = js["meta"]["total_count"]

        # Do the thing
        x = await self._session.get(self.url("/ledger"), auth=self._auth, params=params)
        if x.status_code != 200:
            raise Exception(f"failed to retreive monthly usage {x}")
        js = x.json()

        # Loop through the returned itemized JSON and total
        total = float(0)
        # We only care about > 0 amounts for this since negative are us adding to the balance
        # List comprehension is great
        [
            total := total + (float(i["amount"]) if float(i["amount"]) > 0 else 0)
            for i in js["objects"]
        ]

        return BillingResponse(
            total=total,
            balance=balance,
            start_date=start,
            end_date=end,
        )

    async def get_current_usage(self) -> BillingResponse:
        return await self.get_current_invoiced()

    async def get_invoice(self) -> BillingResponse:
        pass
