from datetime import date, datetime
from typing import TYPE_CHECKING, List

import asyncio
from asgiref.sync import sync_to_async
import boto3
from botocore.exceptions import ClientError

if TYPE_CHECKING:
    from mypy_boto3_ce import Client

from pycloud.base import IaasBase
from pycloud.models import BillingResponse, IaasParam
from pycloud.utils import current_month_date_range
from pycloud import exc


class Amazon(IaasBase):
    access_key: str
    secret_key: str

    _client: "Client"

    @staticmethod
    def params() -> List[IaasParam]:
        return [
            IaasParam(key="access_key", label="Access Key", type="string"),
            IaasParam(key="secret_key", label="Secret Key", type="secret"),
        ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._client = boto3.client(
            "ce",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        )

    async def validate_account(self) -> None:
        def _validate_account():
            try:
                boto3.client(
                    "sts",
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key,
                ).get_caller_identity()
            except Exception as e:
                raise exc.AuthorizationError("Failed to validate account: {}".format(e))

        return await sync_to_async(_validate_account)()

    def _get_billing(self, start: datetime, end: datetime) -> BillingResponse:
        """
        Returns the billing for the given time range.
        """
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ce.html#CostExplorer.Client.get_cost_and_usage
        try:
            # TODO: Wrap in async call
            resp = self._client.get_cost_and_usage(
                TimePeriod={
                    "Start": start.strftime("%Y-%m-%d"),
                    "End": end.strftime("%Y-%m-%d"),
                },
                Granularity="MONTHLY",
                Metrics=["BlendedCost"],
            )
        except ClientError as e:
            raise exc.AuthorizationError("Failed to get Amazon billing: {}".format(e))

        total = resp["ResultsByTime"][0]["Total"]["BlendedCost"]["Amount"]  # type: ignore
        return BillingResponse(
            total=total,  # type: ignore
            balance=None,
            start_date=start,
            end_date=end,
        )

    async def get_current_invoiced(self) -> BillingResponse:
        start, end = current_month_date_range()
        return await sync_to_async(self._get_billing)(start, end)
        return await asyncio.get_running_loop().run_in_executor(
            None, self._get_billing, start, end
        )

    async def get_current_usage(self) -> BillingResponse:
        return await self.get_current_invoiced()

    async def get_invoice(self) -> BillingResponse:
        pass

    async def get_instance_count(self) -> int:
        def _get_server_count() -> int:
            ret = 0
            try:
                rclient = boto3.client(
                    "ec2",
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key,
                    region_name="us-east-1",
                )
                region_resp = rclient.describe_regions()
                regions = [region["RegionName"] for region in region_resp["Regions"]]
                for region in regions:
                    client = boto3.resource(
                        "ec2",
                        aws_access_key_id=self.access_key,
                        aws_secret_access_key=self.secret_key,
                        region_name=region,
                    )
                    instances = client.instances.all()
                    ret += len(
                        [
                            instance
                            for instance in instances
                            if instance.state["Name"] != "terminated"
                        ]
                    )
            except ClientError as e:
                raise exc.AuthorizationError("Failed to get server count: {}".format(e))
            return ret

        return await sync_to_async(_get_server_count)()
