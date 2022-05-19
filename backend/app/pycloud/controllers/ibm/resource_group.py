from datetime import datetime
from typing import List, Any

from pydantic import BaseModel

from .common import BaseResource


class ResourceGroup(BaseModel):
    id: str
    crn: str
    account_id: str
    name: str
    state: str
    default: bool
    enable_reclamation: bool
    quota_id: str
    quota_url: str
    payment_methods_url: str
    resource_linkages: List[Any]
    teams_url: str
    created_at: datetime
    updated_at: datetime


class ListResourceGroupsResp(BaseModel):
    resources: List[ResourceGroup]


class ResourceGroupResource(BaseResource[ResourceGroup]):
    pass
