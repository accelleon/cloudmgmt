from typing import List

from pydantic import BaseModel

from .common import BaseResource
from .cf import CloudFoundry


class Description(BaseModel):
    name: str
    display_name: str


class DevOpsSettings(BaseModel):
    enabled: bool


class Settings(BaseModel):
    devops: DevOpsSettings


class Region(BaseModel):
    id: str
    domain: str
    name: str
    region: str
    display_name: str
    customer: Description
    deployment: Description
    geo: Description
    public_regions_by_proximity: List[str]
    console_url: str
    cf_api: str
    mccp_api: str
    type: str
    home: bool
    aliases: List[str]
    settings: Settings


ListRegionsResp = List[Region]


class RegionResource(BaseResource[Region]):
    async def cf(self) -> CloudFoundry:
        ret = CloudFoundry(self)
        await ret.login()
        return ret
