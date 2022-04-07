from typing import Optional

from pydantic import BaseModel


class AccountFilter(BaseModel):
    id: Optional[int]
    name: Optional[str]
    iaas: Optional[str]


class CreateAccount(BaseModel):
    name: str
    iaas: str
    data: dict


class UpdateAccount(BaseModel):
    name: Optional[str]
    iaas: Optional[str]
    data: Optional[dict]


class Account(CreateAccount):
    id: int

    class Config:
        orm_mode = True
