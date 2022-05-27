from datetime import date, datetime
from typing import TYPE_CHECKING, Iterable, Iterator, List, Optional
import itertools
from itertools import chain

import asyncio
from asgiref.sync import sync_to_async
import boto3
from botocore.exceptions import ClientError

if TYPE_CHECKING:
    from mypy_boto3_ec2.service_resource import Instance, ServiceResourceInstancesCollection

from pycloud.base import IaasBase
from pycloud.models import BillingResponse, IaasParam, VirtualMachine
from pycloud.utils import current_month_date_range, as_async
from pycloud import exc

class Amazon(IaasBase):
    access_key: str
    secret_key: str

    @staticmethod
    def params() -> List[IaasParam]:
        return [
            IaasParam(key="access_key", label="Access Key", type="string"),
            IaasParam(key="secret_key", label="Secret Key", type="secret"),
        ]

    @staticmethod
    def map_instance(instance: "Instance") -> VirtualMachine:
        return VirtualMachine(
            id=instance.id,
            name=instance.id,
            state=instance.state["Name"],
            ip=instance.public_ip_address,
            iaas="Amazon",
        )

    @staticmethod
    def map_instances(instances: Iterable["Instance"]) -> List[VirtualMachine]:
        return [Amazon.map_instance(instance) for instance in instances]

    @as_async
    def validate_account(self) -> None:
        try:
            boto3.client(
                "sts",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
            ).get_caller_identity()
        except Exception as e:
            raise exc.AuthorizationError("Failed to validate account: {}".format(e))

    def _get_billing(self, start: datetime, end: datetime) -> BillingResponse:
        """
        Returns the billing for the given time range.
        """
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ce.html#CostExplorer.Client.get_cost_and_usage
        try:
            client = boto3.client(
                "ce",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
            )
            # TODO: Wrap in async call
            resp = client.get_cost_and_usage(
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

    async def get_current_usage(self) -> BillingResponse:
        return await self.get_current_invoiced()

    async def get_invoice(self) -> BillingResponse:
        pass

    async def get_instance_count(self) -> int:
        return len(await self.get_instances())

    @as_async
    def get_regions(self) -> List[str]:
        rclient = boto3.client(
            "ec2",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name="us-east-1",
        )
        region_resp = rclient.describe_regions()
        return [region["RegionName"] for region in region_resp["Regions"]]

    @as_async
    def _get_instances_in_region(self, region: str, instance_ids: Optional[List[str]] = None) -> "ServiceResourceInstancesCollection":
        client = boto3.resource(
            "ec2",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=region,
        )
        instances = client.instances
        if instance_ids:
            instances = instances.filter(Filters=[{'Name': 'instance-id', 'Values': instance_ids}])
        return instances.all()

    async def _get_instances(self, instance_ids: Optional[List[str]] = None) -> List["Instance"]:
        regions = await self.get_regions()
        instanceList: List["ServiceResourceInstancesCollection"] = (
            await asyncio.gather(
                *[
                    self._get_instances_in_region(region, instance_ids)
                    for region in regions
                ]
            )
        )
        return list(itertools.chain.from_iterable(instanceList))

    async def get_instances(self) -> List[VirtualMachine]:
        return self.map_instances(await self._get_instances())

    async def get_instance(self, instance_id: str) -> Optional[VirtualMachine]:
        instances = await self._get_instances(instance_ids=[instance_id])
        return self.map_instance(instances[0]) if instances else None

    async def delete_instance(self, instance: VirtualMachine) -> None:
        instances = await self._get_instances(instance_ids=[instance.id])
        if instances:
            await sync_to_async(instances[0].terminate)()

    @as_async
    def list_buckets(self) -> List[str]:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        )
        resp = s3.list_buckets()
        return [bucket["Name"] for bucket in resp["Buckets"]]

    @as_async
    def get_whitelist(self, bucket) -> List[str]:
        """
        Returns the whitelist for the given bucket.
        """
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.get_bucket_policy
        try:
            client = boto3.client(
                "s3",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
            )
            resp = client.get_bucket_policy(Bucket=bucket)
            return resp["Policy"]["Statement"][0]["Condition"]["NotIpAddress"]["aws:SourceIp"]
        except ClientError as e:
            raise exc.AuthorizationError("Failed to get bucket policy: {}".format(e))
