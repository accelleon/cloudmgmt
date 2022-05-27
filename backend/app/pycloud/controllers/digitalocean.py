from typing import List

from pycloud.base import IaasBase
from pycloud.models import IaasParam, BillingResponse, VirtualMachine
from pycloud.utils import current_month_date_range
from pycloud import exc


def public_ip(networks):
    for n in networks:
        if n["type"] == "public":
            return n["ip_address"]


class DigitalOcean(IaasBase):
    api_key: str

    @staticmethod
    def params() -> List[IaasParam]:
        return [
            IaasParam(key="api_key", label="Token", type="secret"),
        ]

    def __init__(self, **data):
        super().__init__(**data)
        self._headers.update({"Authorization": f"Bearer {self.api_key}"})
        self._base = "https://api.digitalocean.com/"  # type: ignore

    async def validate_account(self) -> None:
        r = await self._session.get(self.url("/v2/account"), headers=self._headers)
        if r.status_code == 401:
            raise exc.AuthorizationError(
                "Invalid API token. Please check your DigitalOcean credentials."
            )
        if r.status_code != 200:
            raise exc.UnknownError(
                "Failed to get DigitalOcean profile: {}".format(r.text)
            )

    async def _get_current_invoiced(self) -> BillingResponse:
        """
        Returns the invoiced billing for the given month.
        """
        start, end = current_month_date_range()
        r = await self._session.get(
            self.url("/v2/customers/my/invoices"),
            headers=self._headers,
        )
        if r.status_code == 401:
            raise exc.AuthorizationError(
                "Invalid API key. Please check your DigitalOcean API key."
            )
        if r.status_code != 200:
            raise exc.UnknownError(
                "Failed to get DigitalOcean invoices: {}".format(r.text)
            )
        js = r.json()
        total = 0
        for i in js["invoices"]:
            if i["status"] == "paid" and i["date"]["month"] == end.strftime("%Y-%m"):
                total = i["total"]
                break
        else:
            raise exc.UnknownError(
                "No invoices found for the given month: {}".format(
                    end.strftime("%Y-%m")
                )
            )
        return BillingResponse(
            total=total,
            balance=None,
            start_date=start,
            end_date=end,
        )

    async def get_current_invoiced(self) -> BillingResponse:
        """
        Returns the current billing for the current month.
        """
        r = await self._session.get(
            self.url("/v2/customers/my/balance"),
            headers=self._headers,
        )
        if r.status_code == 401:
            raise exc.AuthorizationError(
                "Invalid API key. Please check your DigitalOcean API key."
            )
        if r.status_code != 200:
            raise exc.UnknownError(
                "Failed to get DigitalOcean billing: {}".format(r.text)
            )
        js = r.json()
        start, end = current_month_date_range()
        return BillingResponse(
            total=js["month_to_date_usage"],
            balance=None,
            start_date=start,
            end_date=end,
        )

    async def get_current_usage(self) -> BillingResponse:
        return await self.get_current_invoiced()

    async def get_invoice(self) -> BillingResponse:
        pass

    async def get_instances(self) -> List[VirtualMachine]:
        r = await self._session.get(
            self.url("/v2/droplets"), headers=self._headers
        )
        if r.status_code == 401:
            raise exc.AuthorizationError(
                "Invalid API key. Please check your DigitalOcean API key."
            )
        if r.status_code != 200:
            raise exc.UnknownError(
                "Failed to get DigitalOcean instances: {}".format(r.text)
            )
            return None
        js = r.json()
        return [
            VirtualMachine(
                name=i["name"],
                id=i["id"],
                ip=public_ip(i["networks"]),
                status=i["status"],
                iaas="DigitalOcean",
                tags=i["tags"],
            )
            for i in js["droplets"]
        ]

    async def get_instance_count(self) -> int:
        r = await self._session.get(self.url("/v2/droplets"), headers=self._headers)
        if r.status_code == 401:
            raise exc.AuthorizationError(
                "Invalid API key. Please check your DigitalOcean API key."
            )
        if r.status_code != 200:
            raise exc.UnknownError(
                "Failed to get DigitalOcean droplets: {}".format(r.text)
            )
        js = r.json()
        return js["meta"]["total"]

    async def get_instance(self, instance_id: str) -> VirtualMachine:
        r = await self._session.get(
            self.url("/v2/droplets/{}".format(instance_id)), headers=self._headers
        )
        if r.status_code == 401:
            raise exc.AuthorizationError(
                "Invalid API key. Please check your DigitalOcean API key."
            )
        if r.status_code != 200:
            raise exc.UnknownError(
                "Failed to get DigitalOcean instance: {}".format(r.text)
            )
        js = r.json()
        return VirtualMachine(
            name=js["name"],
            id=js["id"],
            ip=public_ip(js["networks"]),
            status=js["status"],
            iaas="DigitalOcean",
            tags=js["tags"],
        )

    async def delete_instance(self, instance: VirtualMachine) -> None:
        r = await self._session.delete(
            self.url("/v2/droplets/{}".format(instance.id)), headers=self._headers
        )
        if r.status_code == 401:
            raise exc.AuthorizationError(
                "Invalid API key. Please check your DigitalOcean API key."
            )
        if r.status_code != 204:
            raise exc.UnknownError(
                "Failed to delete DigitalOcean instance: {}".format(r.text)
            )
