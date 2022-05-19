from typing import List
from datetime import datetime

from pydantic import BaseModel

from .common import Pagination, BaseResource
from .user import User
from .resource_group import ListResourceGroupsResp, ResourceGroupResource
from .coe import COEDescription


class LinkedAccount(BaseModel):
    origin: str
    id: str
    url: str


class Owner(BaseModel):
    ibmid: str
    url: str


class Resource(BaseModel):
    total: int
    url: str


class AccountEntity(BaseModel):
    name: str
    state: str
    sub_state: str
    primary_owner: Owner
    owner_unique_id: str
    owner_iam_id: str
    country_code: str
    team_directory_enabled: bool
    subscriptions: Resource
    traits: Resource


class AccountMetadata(BaseModel):
    guid: str
    url: str
    created_at: datetime
    updated_at: datetime
    origin: str
    linked_accounts: List[LinkedAccount]


class Account(BaseModel):
    metadata: AccountMetadata
    entity: AccountEntity


class AccountResource(BaseResource[Account]):
    async def get_user(self) -> User:
        r = await self.parent.client.get(
            f"https://accounts.cloud.ibm.com/{self.me.metadata.url}/{self.me.entity.owner_iam_id}",
            headers=self.parent.headers,
            params={
                "include_linkages": True,
            },
        )
        if r.status_code != 200:
            raise Exception(f"get_user failed: {r.text}")
        return User(**r.json())

    async def get_resource_groups(self) -> List[ResourceGroupResource]:
        r = await self.parent.client.get(
            "https://resource-controller.cloud.ibm.com/v2/resource-groups",
            headers=self.parent.headers,
            params={
                "account_id": self.me.metadata.guid,
            },
        )
        if r.status_code != 200:
            raise Exception(f"get_resource_groups failed: {r.text}")
        return [ResourceGroupResource(me=r, parent=self.parent) for r in ListResourceGroupsResp(**r.json()).resources]

    async def get_coe(self) -> COEDescription:
        r = await self.parent.client.get(
            f"https://accounts.cloud.ibm.com/coe/v2/accounts/{self.me.metadata.guid}",
            headers=self.parent.headers,
        )
        if r.status_code != 200:
            raise Exception(f"get_coe failed: {r.text}")
        return COEDescription(**r.json())


class ListAccountResp(Pagination[Account]):
    pass
