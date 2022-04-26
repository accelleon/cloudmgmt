from typing import Optional
import re

from pydantic import BaseModel, validator
from app.model.common import SearchQueryBase, SearchResponse

from pycloud.models import BillingResponse
from .account import Account


class BillingPeriodFilter(BaseModel):
    period: str
    iaas: Optional[str] = None
    account: Optional[str] = None

    @validator("period")
    def validate_period(cls, v):
        if v is None:
            raise ValueError("period is required")
        # match regex pattern
        if not re.match(r"^\d{4}-\d{2}$", v):
            raise ValueError("Invalid period format")
        return v


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
