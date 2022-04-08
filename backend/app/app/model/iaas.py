from enum import Enum
from typing import TYPE_CHECKING, List

from pydantic import BaseModel

if TYPE_CHECKING:
    from .account import Account


class IaasType(Enum):
    IAAS = "IAAS"
    PAAS = "PAAS"


class IaasDesc(BaseModel):
    name: str
    type: IaasType
    params: List[str]


class Iaas(IaasDesc):
    id: int

    accounts: 'List[Account]'

    class Config:
        orm_mode = True
