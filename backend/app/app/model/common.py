from typing import Optional, TypeVar, Any, List

from pydantic import BaseModel


FilterType = TypeVar("FilterType", bound="BaseModel")


class SearchQueryBase(BaseModel):
    page: int = 0
    per_page: int = 20
    sort: Optional[str] = None


class SearchResponse(BaseModel):
    results: List[Any]
    page: int
    per_page: int
    total: int
    next: Optional[str] = None
    prev: Optional[str] = None


# Generic failure response
class FailedResponse(BaseModel):
    detail: str
