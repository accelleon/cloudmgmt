from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel

from .common import SearchQueryBase, SearchResponse


if TYPE_CHECKING:
    from .account import _Account


class IaasType(Enum):
    IAAS = "IAAS"
    PAAS = "PAAS"


class IaasFilter(BaseModel):
    name: Optional[str] = None
    type: Optional[IaasType] = None


class IaasDesc(BaseModel):
    name: str
    type: IaasType
    params: List[str]


# Avoid recursion on cyclic models
class _Iaas(IaasDesc):
    id: int

    class Config:
        orm_mode = True


class Iaas(_Iaas):
    accounts: List["_Account"]


class IaasSearchRequest(SearchQueryBase, IaasFilter):
    sort: str = "name"


class IaasSearchResponse(SearchResponse[Iaas]):
    pass
