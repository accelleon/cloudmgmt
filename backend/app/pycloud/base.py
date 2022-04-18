from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Type

from pydantic import BaseModel, AnyHttpUrl
from requests import Session
from urllib.parse import urljoin

from .models import IaasType, IaasParam, BillingResponse


session: Optional[Session] = None


class ProviderBase(BaseModel, ABC):
    _session: Session
    _id: int
    _base: AnyHttpUrl
    _headers: Dict[str, str] = {}

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

    def currency(self) -> str:
        return "USD"

    def url(self, path: str) -> str:
        return urljoin(self._base, path)

    def __init__(self, **kwargs):  # type: ignore
        super().__init__(**kwargs)
        global session
        if not session:
            session = Session()
        self._session = session
        self._headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    @abstractmethod
    def get_current_billing(self) -> BillingResponse:
        pass


class IaasBase(ProviderBase):
    @staticmethod
    def type() -> IaasType:
        return IaasType.IAAS


class PaasBase(ProviderBase):
    @staticmethod
    def type() -> IaasType:
        return IaasType.PAAS
