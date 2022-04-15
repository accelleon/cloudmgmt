from enum import Enum
from typing import List, Optional, Literal

from pydantic import BaseModel, root_validator


class IaasType(Enum):
    IAAS = "IAAS"
    PAAS = "PAAS"


class IaasParam(BaseModel):
    key: str
    label: str
    type: Literal["string", "choice", "secret"] = "string"
    choices: Optional[List[str]] = None

    @root_validator()
    def validator(cls, values):
        if values.get("type") == "choice" and not values.get("choices"):
            raise ValueError("choices must be provided for choice type")
        return values


class IaasDesc(BaseModel):
    name: str
    type: IaasType
    params: List[IaasParam]
