from abc import ABC, abstractmethod
from typing import List, Dict, Optional

from pydantic import BaseModel, AnyHttpUrl
from httpx import AsyncClient
from urllib.parse import urljoin

from .models import IaasType, IaasParam, BillingResponse


session: Optional[AsyncClient] = None


class ProviderBase(BaseModel, ABC):
    _session: AsyncClient
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        global session
        if not session:
            session = AsyncClient()
        self._session = session
        self._headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    @abstractmethod
    async def get_current_billing(self) -> BillingResponse:
        pass


class IaasBase(ProviderBase):
    @staticmethod
    def type() -> IaasType:
        return IaasType.IAAS


class PaasBase(ProviderBase):
    @staticmethod
    def type() -> IaasType:
        return IaasType.PAAS
