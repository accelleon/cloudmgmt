from typing import Optional, Dict

from pydantic import BaseModel

from pycloud.factory import CloudFactory
from pycloud.models import IaasType
from .common import SearchQueryBase, SearchResponse
from .iaas import Iaas, _Iaas


class AccountFilter(BaseModel):
    name: Optional[str] = None
    iaas: Optional[str] = None
    type: Optional[IaasType] = None
    group: Optional[str] = None


class CreateAccount(BaseModel):
    name: str
    iaas: str
    data: Dict[str, str]
    group: str


class UpdateAccount(BaseModel):
    name: Optional[str] = None
    data: Optional[Dict[str, str]] = None
    group: Optional[str] = None


AccountData = CloudFactory.get_pub_data_model()


# HACK: FastAPI by default uses exclude_none=False
# override the dict() method to exclude None values
def dict_none(self, *args, **kwargs):
    kwargs["exclude_none"] = True
    return BaseModel.dict(self, *args, **kwargs)


setattr(AccountData, "dict", dict_none)


# To avoid the recursion on cyclic models
class _Account(BaseModel):
    id: Optional[int] = None
    name: str
    iaas_id: int
    currency: str
    data: AccountData  # type: ignore
    validated: bool
    last_error: Optional[str]

    class Config:
        orm_mode = True


class Account(_Account):
    iaas: _Iaas


class AccountSearchRequest(SearchQueryBase, AccountFilter):
    sort: str = "name"


class AccountSearchResponse(SearchResponse[Account]):
    pass


Iaas.update_forward_refs(_Account=_Account)
