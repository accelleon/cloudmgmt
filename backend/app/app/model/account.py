from typing import Optional, Dict

from pydantic import BaseModel

from .iaas import Iaas


class AccountFilter(BaseModel):
    name: Optional[str]
    iaas: Optional[str]


class CreateAccount(BaseModel):
    name: str
    iaas: str
    data: Dict[str, str]


class UpdateAccount(AccountFilter):
    name: Optional[str] = None
    data: Optional[Dict[str, str]]


class Account(BaseModel):
    id: Optional[int]
    name: str
    iaas: Iaas
    data: Dict[str, str]

    class Config:
        orm_mode = True


Iaas.update_forward_refs(Account=Account)
