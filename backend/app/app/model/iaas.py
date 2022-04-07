from typing import List
from enum import Enum

from pydantic import BaseModel, Json


class IaasType(Enum):
    IAAS = "IAAS"
    PAAS = "PAAS"


class IaasOption(BaseModel):
    name: str
    type: str
    secret: bool


class CreateIaas(BaseModel):
    name: str
    type: IaasType
    parameters: List[IaasOption]


class Iaas(CreateIaas):
    id: int

    class Config:
        orm_mode = True
