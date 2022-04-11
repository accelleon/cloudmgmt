from typing import Optional, Dict, List

from pydantic import BaseModel

from .common import SearchQueryBase, SearchResponse
from .iaas import Iaas


class AccountFilter(BaseModel):
    name: Optional[str] = None
    iaas: Optional[str] = None


class CreateAccount(BaseModel):
    name: str
    iaas: str
    data: Dict[str, str]


class UpdateAccount(BaseModel):
    name: Optional[str] = None
    data: Optional[Dict[str, str]] = None


class Account(BaseModel):
    id: Optional[int] = None
    name: str
    iaas: Iaas
    data: Dict[str, str]

    class Config:
        orm_mode = True


class AccountSearchRequest(SearchQueryBase, AccountFilter):
    sort: str = "name"


class AccountSearchResponse(SearchResponse):
    results: List[Account]
