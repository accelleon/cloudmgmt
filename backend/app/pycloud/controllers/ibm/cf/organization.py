from typing import Optional, List

from pydantic import BaseModel

from .common import Metadata, BaseResource
from ..common import Pagination
from .space import SpaceResource, ListSpacesResp


class OrganizationEntity(BaseModel):
    name: str
    billing_enabled: bool
    quota_definition_guid: str
    status: str
    default_isolation_segment_guid: Optional[str]
    quota_definition_url: str
    spaces_url: str
    domains_url: str
    private_domains_url: str
    users_url: str
    managers_url: str
    billing_managers_url: str
    auditors_url: str
    app_events_url: str
    space_quota_definitions_url: str


class Organization(BaseModel):
    metadata: Metadata
    entity: OrganizationEntity


class ListOrganiztionsResp(Pagination[Organization]):
    pass


class OrganizationResource(BaseResource[Organization]):
    async def get_spaces(self) -> List[SpaceResource]:
        r = await self.parent.client.get(
            f"{self.region.cf_api}/{self.me.entity.spaces_url}",
            headers=self.parent.headers,
        )
        if r.status_code != 200:
            raise Exception(r.text)
        return SpaceResource.map_model(
            ListSpacesResp(**r.json()).resources, parent=self.parent, region=self.region
        )
