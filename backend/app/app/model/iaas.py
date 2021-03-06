from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel

from pycloud.models import IaasType, IaasDesc
from .common import SearchQueryBase, SearchResponse


if TYPE_CHECKING:
    from .account import _Account  # noqa


class IaasFilter(BaseModel):
    name: Optional[str] = None
    type: Optional[IaasType] = None


# Avoid recursion on cyclic models
class _Iaas(IaasDesc):
    id: int

    class Config:
        orm_mode = True


class Iaas(_Iaas):
    # accounts: List["_Account"]
    pass


class IaasSearchRequest(SearchQueryBase, IaasFilter):
    sort: str = "name"


class IaasSearchResponse(SearchResponse[Iaas]):
    pass
