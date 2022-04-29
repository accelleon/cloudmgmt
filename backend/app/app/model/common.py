from typing import Optional, TypeVar, List, Generic
from enum import Enum

from pydantic import BaseModel
from pydantic.generics import GenericModel


RespType = TypeVar("RespType", bound="BaseModel")


class SearchOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class SearchQueryBase(BaseModel):
    page: int = 0
    per_page: int = 0
    sort: Optional[str] = None
    order: SearchOrder = SearchOrder.ASC


class SearchResponse(GenericModel, Generic[RespType]):
    results: List[RespType]
    page: int
    per_page: int
    total: int
    order: SearchOrder
    next: Optional[str] = None
    prev: Optional[str] = None


# Generic failure response
class FailedResponse(BaseModel):
    detail: str
