from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Dict
from pydantic import BaseModel
from requests import Session

from .models import IaasType, IaasParam

if TYPE_CHECKING:
    from app.model.billing import CreateBillingPeriod


class ProviderBase(BaseModel, ABC):
    _session: Session
    _id: int

    class Config:
        underscore_attrs_are_private = True

    @staticmethod
    @abstractmethod
    def type() -> IaasType:
        pass

    @staticmethod
    @abstractmethod
    def params() -> List[IaasParam]:
        pass

    @classmethod
    @abstractmethod
    def check_params(cls, data: Dict[str, str]) -> None:
        pass

    def __init__(self, id: int = 0, **kwargs):  # type: ignore
        super().__init__(**kwargs)
        self._id = id
        self._session = Session()

    @abstractmethod
    async def get_current_billing(self) -> "CreateBillingPeriod":
        pass


class IaasBase(ProviderBase):
    @staticmethod
    def type() -> IaasType:
        return IaasType.IAAS


class PaasBase(ProviderBase):
    @staticmethod
    def type() -> IaasType:
        return IaasType.PAAS
