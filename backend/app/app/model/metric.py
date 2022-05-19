from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel

from .account import Account


class MetricFilter(BaseModel):
    iaas: Optional[str] = None
    account: Optional[str] = None
    granularity: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class Metric(BaseModel):
    account_id: int
    instances: int
    time: datetime


class MetricResponse(BaseModel):
    results: List[Metric]
    granularity: str
    start_date: datetime
    end_date: datetime
