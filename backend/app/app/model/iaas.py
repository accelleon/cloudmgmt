from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from .common import SearchQueryBase, SearchResponse


class IaasType(Enum):
    IAAS = "IAAS"
    PAAS = "PAAS"


class IaasDesc(BaseModel):
    name: str
    type: IaasType
    params: List[str]


class Iaas(IaasDesc):
    id: int

    class Config:
        orm_mode = True


class IaasQuery(BaseModel):
    name: Optional[str] = None
    type: Optional[IaasType] = None


class IaasFilter(SearchQueryBase, IaasQuery):
    sort: str = "name"


class IaasSearchResponse(SearchResponse):
    results: List[Iaas]
