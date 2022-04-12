from typing import Optional, Dict

from pydantic import BaseModel

from .common import SearchQueryBase, SearchResponse
from .iaas import Iaas, _Iaas


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


# To avoid the recursion on cyclic models
class _Account(BaseModel):
    id: Optional[int] = None
    name: str
    iaas_id: int
    data: Dict[str, str]

    class Config:
        orm_mode = True


class Account(_Account):
    iaas: _Iaas


class AccountSearchRequest(SearchQueryBase, AccountFilter):
    sort: str = "name"


class AccountSearchResponse(SearchResponse[Account]):
    pass


Iaas.update_forward_refs(_Account=_Account)
