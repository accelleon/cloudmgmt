from typing import Optional
from datetime import datetime

from pydantic import BaseModel
from app.model.common import SearchQueryBase, SearchResponse

from pycloud.models import BillingResponse
from .account import Account


class BillingPeriodFilter(BaseModel):
    iaas: Optional[str] = None
    account: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class UpdateBillingPeriod(BaseModel):
    total: Optional[float] = None
    balance: Optional[float] = None


class CreateBillingPeriod(BillingResponse):
    account_id: int


class _BillingPeriod(CreateBillingPeriod):
    id: int

    class Config:
        orm_mode = True


class BillingPeriod(_BillingPeriod):
    account: Account


class BillingSearchRequest(SearchQueryBase, BillingPeriodFilter):
    pass


class BillingSearchResponse(SearchResponse[BillingPeriod]):
    pass
