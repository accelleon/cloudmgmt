from typing import Optional, TypeVar, List, Generic
from enum import Enum

from fastapi import Request

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

    @classmethod
    def from_results(cls, *, pagination: SearchQueryBase, results: List[RespType], total: int, request: Request) -> "SearchResponse[RespType]":
        ret = cls(
            **pagination.dict(exclude_unset=False),
            results=results,
            total=total
        )
        params = pagination.dict(exclude_unset=False)
        if total > pagination.per_page * (pagination.page + 1):
            params["page"] = pagination.page + 1
            ret.next = str(request.url.replace_query_params(**params))
        if pagination.page > 0:
            params["page"] = pagination.page - 1
            ret.prev = str(request.url.replace_query_params(**params))
        return ret


# Generic failure response
class FailedResponse(BaseModel):
    detail: str
