from typing import List, Optional

from pydantic import BaseModel
from .account import Account
from .common import SearchResponse


class CreateGroup(BaseModel):
    name: str


class FilterGroup(BaseModel):
    name: Optional[str] = None


class UpdateGroup(FilterGroup):
    name: Optional[str] = None
    account_ids: Optional[List[int]] = None


class FilterGroup(UpdateGroup):
    name: Optional[str] = None


class _Group(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class Group(_Group):
    accounts: List[Account]


class GroupSearchResponse(SearchResponse[Group]):
    pass
