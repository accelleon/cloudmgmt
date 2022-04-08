from abc import ABC, abstractmethod
from typing import List, Dict, Any, TypeVar, Type

from pydantic import BaseModel, SecretStr

from app.model.iaas import IaasType


class ProviderBase(BaseModel, ABC):
    class Config:
        json_encoders = {SecretStr: lambda v: v.get_secret_value() if v else None}
        underscore_attrs_are_private = True

    @staticmethod
    @abstractmethod
    def type() -> IaasType:
        pass
