from typing import List, Any, Tuple
import json

from dateutil.relativedelta import relativedelta

from pycloud.base import PaasBase
from pycloud.models import IaasParam, BillingResponse
from pycloud import exc

from .ibm import IBMApi

# item for usage costs
api_getNextInvoiceTopLevel = "https://api.softlayer.com/rest/v3.1/SoftLayer_Account/getNextInvoiceTopLevelBillingItems.json"

# Grab child items of a billing item
# Returns only non-zero cost children of billing item id {id}
api_getChildren = "https://api.softlayer.com/rest/v3.1/SoftLayer_Billing_Item/{id}/getNonZeroNextInvoiceChildren.json"

# Grab previous invoice object
api_getPrevInvoice = "https://api.softlayer.com/rest/v3.1/SoftLayer_Account/getLatestRecurringInvoice.json"

# Grab top level items of indicated invoice
api_getInvoiceTopLevel = "https://api.softlayer.com/rest/v3.1/SoftLayer_Billing_Invoice/{id}/getInvoiceTopLevelItems.json"

# Grab an invoices non-zero cost children
api_getInvoiceChildren = "https://api.softlayer.com/rest/v3.1/SoftLayer_Billing_Invoice_Item/{id}/getNonZeroAssociatedChildren.json"


class Bluemix(PaasBase):
    account_name: str
    sl_apikey: str
    ibm_apikey: str

    _auth: Tuple[str, str]
    _filter: str = "^=paas"
    _api: IBMApi

    @staticmethod
    def params() -> List[IaasParam]:
        return [
            IaasParam(key="account_name", label="Account Number", type="string"),
            IaasParam(key="sl_apikey", label="SL API Key", type="secret"),
            IaasParam(key="ibm_apikey", label="Bluemix API Key", type="secret"),
        ]

    def __init__(self, **data):
        super().__init__(**data)
        self._base = "https://api.softlayer.com/"
        self._auth = (self.account_name, self.sl_apikey)
        self._api = IBMApi(self.ibm_apikey, client=self._session)

    async def validate_account(self) -> None:
        r = await self._session.get(
            self.url("/rest/v3.1/SoftLayer_Account/getCurrentUser.json"),
            auth=self._auth,
        )
        if r.status_code != 200:
            raise exc.AuthorizationError(
                "Invalid API key. Please check your Softlayer Account number or API key."
            )
        try:
            await self._api.login()
        except Exception as e:
            raise exc.AuthorizationError(
                "Invalid API key. Please check your Bluemix API key.", e
            )

    async def _get_invoices(self) -> Any:
        r = await self._session.get(
            self.url("/rest/v3.1/Softlayer_Account/getInvoices"),
            auth=self._auth,
        )
        if r.status_code == 401:
            raise exc.AuthorizationError(
                "Invalid API key. Please check your Softlayer API key."
            )
        if r.status_code != 200:
            raise exc.UnknownError(
                "Failed to get Softlayer invoices: {}".format(r.text)
            )
        return r.json()

    async def get_current_invoiced(self) -> BillingResponse:
        # We filter everything that doesn't start with paas
        # Object filters suck https://sldn.softlayer.com/article/object-filters/
        objectFilter = {
            "invoiceTopLevelItems": {"categoryCode": {"operation": self._filter}}
        }

        # These are the parameters we'll pass to the request
        # Include the object filter as a json dump, its neater to do it this way
        # Object masks are better than filters https://sldn.softlayer.com/article/object-masks/
        paramsTopLevel = {
            "objectMask": "mask[id,categoryCode,recurringFee,billingItemId]",
            "objectFilter": json.dumps(objectFilter),
        }

        # Grab the previous invoice
        x = await self._session.get(api_getPrevInvoice, auth=self._auth)
        js = json.loads(x.text)
        if x.status_code != 200:
            raise Exception(f"getPrevInvoice Failed:\n{json.dumps(js, indent=4)}")
        # Bluemix/softlayer return an empty response if there isn't one
        if not js:
            raise Exception("No previous invoice found")
        # Need id and invoice creation date (billing period end date)
        invoice = js["id"]
        endDate = js["createDate"]

        # Pull top level items for that invoice
        x = await self._session.get(
            api_getInvoiceTopLevel.format(id=invoice),
            auth=self._auth,
            params=paramsTopLevel,
        )
        topLevel = json.loads(x.text)
        if x.status_code != 200:
            raise Exception(
                f"getInvoiceTopLevel Failed:\n{json.dumps(topLevel, indent=4)}"
            )

        # Mask for calls to getChildren
        paramsChildren = {"objectMask": "mask[recurringFee]"}

        total = 0.0
        # Loop through every top level item and pull the cost for its children
        for item in topLevel:
            total += float(item["recurringFee"])
            x = await self._session.get(
                api_getInvoiceChildren.format(id=item["id"]),
                auth=self._auth,
                params=paramsChildren,
            )
            children = json.loads(x.text)
            if x.status_code != 200:
                raise Exception(
                    f"getChildren Failed:\n{json.dumps(children, indent=4)}"
                )
            for child in children:
                total += float(child["recurringFee"])

        resp = BillingResponse(
            total=total,
            start_date=endDate,
            end_date=endDate,
        )
        resp.start_date = resp.start_date - relativedelta(months=1)
        return resp

    async def get_current_usage(self) -> BillingResponse:
        # We filter everything that doesn't start with paas
        # Object filters suck https://sldn.softlayer.com/article/object-filters/
        objectFilter = {
            "nextInvoiceTopLevelBillingItems": {
                "categoryCode": {"operation": self._filter}
            }
        }

        # These are the parameters we'll pass to the request
        # Include the object filter as a json dump, its neater to do it this way
        # Object masks are better than filters https://sldn.softlayer.com/article/object-masks/
        paramsTopLevel = {
            "objectMask": "mask[id,categoryCode,recurringFee,cycleStartDate,nextBillDate]",
            "objectFilter": json.dumps(objectFilter),
        }

        x = await self._session.get(
            api_getNextInvoiceTopLevel, auth=self._auth, params=paramsTopLevel
        )
        topLevel = json.loads(x.text)
        if x.status_code != 200:
            raise Exception(
                f"getNextInvoiceTopLevel Failed:\n{json.dumps(topLevel, indent=4)}"
            )

        startDate = None
        endDate = None
        if topLevel:
            startDate = topLevel[0]["cycleStartDate"]
            endDate = topLevel[0]["nextBillDate"]

        # Mask for calls to getChildren
        paramsChildren = {"objectMask": "mask[recurringFee]"}

        total = 0.0

        # Loop through every top level item and pull the cost for its children
        for item in topLevel:
            total += float(item["recurringFee"])
            x = await self._session.get(
                api_getChildren.format(id=item["id"]),
                auth=self._auth,
                params=paramsChildren,
            )
            children = json.loads(x.text)
            if x.status_code != 200:
                raise Exception(
                    f"getChildren Failed:\n{json.dumps(children, indent=4)}"
                )
            for child in children:
                total += float(child["recurringFee"])

        return BillingResponse(
            total=total,
            start_date=startDate,
            end_date=endDate,
        )

    async def get_invoice(self) -> BillingResponse:
        raise NotImplementedError()

    async def get_instance_count(self) -> int:
        await self._api.login()
        regions = await self._api.get_regions()
        ret = 0
        for region in regions:
            cf = region.cf()
            try:
                await cf.login()
                orgs = await cf.get_organizations()
                for org in orgs:
                    spaces = await org.get_spaces()
                    for space in spaces:
                        ret += len((await space.get_info()).apps)
            except NotImplementedError:
                pass
        return ret
