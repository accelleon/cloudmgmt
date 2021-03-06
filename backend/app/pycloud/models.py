from enum import Enum
from typing import List, Optional, Literal, Any
from datetime import datetime

from pydantic import BaseModel, root_validator


class BillingResponse(BaseModel):
    start_date: datetime
    end_date: datetime
    total: float
    balance: Optional[float]

    @root_validator()
    def round_floats(cls, values):
        values["total"] = round(values["total"], 2)
        if "balance" in values and values["balance"]:
            values["balance"] = round(values["balance"], 2)
        return values


class IaasType(Enum):
    IAAS = "IAAS"
    PAAS = "PAAS"
    SIP = "SIP"


class VirtualMachine(BaseModel):
    metadata: Any
    id: str
    name: str
    iaas: str
    ip: Optional[str]
    state: str
    tags: List[str] = []


class IaasParam(BaseModel):
    key: str
    label: str
    type: Literal["string", "choice", "secret"] = "string"
    choices: Optional[List[str]] = None
    readonly: bool = False

    @root_validator()
    def validator(cls, values):
        if values.get("type") == "choice" and not values.get("choices"):
            raise ValueError("choices must be provided for choice type")
        return values


class IaasDesc(BaseModel):
    name: str
    type: IaasType
    params: List[IaasParam]
