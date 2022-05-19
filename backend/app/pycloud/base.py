from abc import ABC, abstractmethod
from typing import List, Dict, Optional

from pydantic import BaseModel, AnyHttpUrl
from httpx import AsyncClient, AsyncHTTPTransport
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
            transport = AsyncHTTPTransport(retries=5)
            session = AsyncClient(transport=transport, follow_redirects=True)
        self._session = session
        self._headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    @abstractmethod
    async def validate_account(self) -> None:
        pass

    @abstractmethod
    async def get_current_invoiced(self) -> BillingResponse:
        """
        Returns the current invoiced billing for the current month.
        This will only aggregate costs that have actually invoiced.
        """
        pass

    @abstractmethod
    async def get_current_usage(self) -> BillingResponse:
        """
        Returns the current estimated billing for the current month.
        This will aggregate costs that are also not invoiced yet.
        Note that for some providers this is the same as the current invoiced.
        """
        pass

    @abstractmethod
    async def get_invoice(self) -> BillingResponse:
        """
        Returns a filetype and bytestream for the invoice for a given month.
        The filetype will vary from provider to provider. For example, rackspace returns a CSV,
        DO has a PDF.
        """
        pass


class CloudBase(ProviderBase, ABC):
    pass


class SIPBase(ProviderBase):
    @staticmethod
    def type() -> IaasType:
        return IaasType.SIP


class IaasBase(CloudBase):
    @staticmethod
    def type() -> IaasType:
        return IaasType.IAAS

    @abstractmethod
    async def get_instance_count(self) -> int:
        pass


class PaasBase(CloudBase):
    @staticmethod
    def type() -> IaasType:
        return IaasType.PAAS

    @abstractmethod
    async def get_instance_count(self) -> int:
        pass
