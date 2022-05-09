from typing import List

from pycloud.base import IaasBase
from pycloud.models import BillingResponse, IaasParam
from pycloud import exc


auth_endpoint = "https://login.microsoftonline.com/{tenant_id}/oauth2/token"
usage_endpoint = "https://management.azure.com/subscriptions/{subscriptionId}/providers/Microsoft.Consumption/usageDetails"
period_endpoint = "https://management.azure.com/subscriptions/{subscriptionId}/providers/Microsoft.Billing/billingPeriods?api-version=2017-04-24-preview"


class Azure(IaasBase):
    subscription_id: str
    tenant_id: str
    client_id: str
    client_secret: str

    @staticmethod
    def params() -> List[IaasParam]:
        return [
            IaasParam(key="subscription_id", label="Subscription ID", type="string"),
            IaasParam(key="tenant_id", label="Tenant ID", type="string"),
            IaasParam(key="client_id", label="Client ID", type="string"),
            IaasParam(key="client_secret", label="Client Secret", type="secret"),
        ]

    def __init__(self, **data):
        super().__init__(**data)
        self._base = "https://management.azure.com/"

    async def authenticate(self) -> None:
        # Build payload for authentication
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "resource": "https://management.azure.com/",
        }

        # Do the auth, grab the token
        x = await self._session.post(
            auth_endpoint.format(tenant_id=self.tenant_id), data=data
        )
        js = x.json()
        if x.status_code != 200:
            raise exc.AuthorizationError(f"authentication failed:\n{x.text}")
        token = js["access_token"]
        self._headers.update({"Authorization": f"Bearer {token}"})

    async def validate_account(self) -> None:
        await self.authenticate()

    async def get_current_invoiced(self) -> BillingResponse:
        await self.authenticate()
        # Parameters for the initial request
        params = {
            # Microsoft, thats all I have to say
            "api-version": "2021-10-01",
            # This is required to get information for the current billing period
            "$expand": "properties/meterDetails",
        }

        # This is the initial request, you could just manually append the parameters
        # to the URL but this is easier to change
        # We're just building the URL and makes looping later cleaner
        p = self._session.build_request(
            "GET",
            usage_endpoint.format(subscriptionId=self.subscription_id),
            params=params,
        )
        next_url = p.url

        startDate = None
        endDate = None

        total = 0
        # We loop here to handle pagination
        while next_url is not None:
            # We already appended the parameters above
            x = await self._session.get(next_url, headers=self._headers)
            js = x.json()
            if x.status_code != 200:
                raise exc.UnknownError(f"failed to get usage:\n{x.text}")

            # Loop through the returned itemized JSON and total
            [total := total + i["properties"]["paygCostInUSD"] for i in js["value"]]

            # If we haven't grabbed the billing start and end dates do so now
            if startDate is None and js["value"]:
                startDate = js["value"][0]["properties"]["servicePeriodStartDate"]
                endDate = js["value"][0]["properties"]["servicePeriodEndDate"]

            # Check if there is another page
            if "nextLink" in js.keys():
                # Yep, make this the request
                next_url = js["nextLink"]
            else:
                # Nope break the loop
                break

        return BillingResponse(
            start_date=startDate,
            end_date=endDate,
            total=total,
        )

    async def get_current_usage(self) -> BillingResponse:
        return await self.get_current_invoiced()

    async def get_invoice(self) -> BillingResponse:
        pass
