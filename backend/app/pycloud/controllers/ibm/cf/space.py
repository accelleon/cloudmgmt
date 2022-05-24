from typing import List, Optional, Any

from pydantic import BaseModel

from ..common import Pagination
from .common import Metadata, BaseResource
from .app import App


class SpaceEntity(BaseModel):
    name: str
    organization_guid: str
    space_quota_definition_guid: Optional[str]
    isolation_segment_guid: Optional[str]
    allow_ssh: bool
    organization_url: str
    developers_url: str
    managers_url: str
    auditors_url: str
    apps_url: str
    routes_url: str
    domains_url: str
    service_instances_url: str
    app_events_url: str
    events_url: str
    security_groups_url: str
    staging_security_groups_url: str


class Space(BaseModel):
    metadata: Metadata
    entity: SpaceEntity


class ListSpacesResp(Pagination[Space]):
    pass


class SummaryResp(BaseModel):
    guid: str
    name: str
    apps: List[App]
    services: List[Any]


class SpaceResource(BaseResource[Space]):
    async def get_info(self) -> SummaryResp:
        r = await self.parent.client.get(
            f"{self.region.cf_api}/{self.me.metadata.url}/summary",
            headers=self.parent.headers,
        )
        if r.status_code != 200:
            raise Exception(r.text)
        return SummaryResp(**r.json())
