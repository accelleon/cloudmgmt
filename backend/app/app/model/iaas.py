from enum import Enum
from typing import TYPE_CHECKING, List, Optional, Literal

from pydantic import BaseModel, root_validator

from .common import SearchQueryBase, SearchResponse


if TYPE_CHECKING:
    from .account import _Account


class IaasType(Enum):
    IAAS = "IAAS"
    PAAS = "PAAS"


class IaasParam(BaseModel):
    key: str
    label: str
    type: Literal["string", "choice", "secret"] = "string"
    choices: Optional[List[str]] = None

    @root_validator()
    def validator(cls, values):
        if values.get("type") == "choice" and not values.get("choices"):
            raise ValueError("choices must be provided for choice type")
        return values


class IaasFilter(BaseModel):
    name: Optional[str] = None
    type: Optional[IaasType] = None


class IaasDesc(BaseModel):
    name: str
    type: IaasType
    params: List[IaasParam]


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
