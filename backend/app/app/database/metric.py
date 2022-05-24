from tokenize import group
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

from sqlalchemy import JSON, select, Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import Select
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession as Session
import pandas as pd
import numpy as np

from .base import Base, CRUDBase
from .account import Account  # noqa
from .iaas import Iaas, IaasType


class CloudMetric(Base):
    __tablename__ = "cloud_metric"
    id: int = Column(Integer, primary_key=True, index=True)
    account_id: int = Column(
        Integer, ForeignKey("account.id", ondelete="CASCADE"), nullable=False
    )
    time: datetime = Column(DateTime(timezone=True), nullable=False)
    instances: int = Column(Integer, nullable=False)

    account: Account = relationship("Account", lazy="selectin")

    def __repr__(self):
        return f"CloudMetric(id={self.id!r}, account_id={self.account_id!r}, time={self.time!r})"


class MetricService:
    async def get(self, db: Session, id: int) -> Optional[CloudMetric]:
        return (
            (await db.execute(select(CloudMetric).where(CloudMetric.id == id)))
            .scalars()
            .first()
        )

    async def create(
        self, db: Session, *, account_id: int, time: datetime, instances: int
    ) -> CloudMetric:
        metric = CloudMetric(
            account_id=account_id,
            time=time,
            instances=instances,
        )
        db.add(metric)
        await db.commit()
        await db.refresh(metric)
        return metric

    async def filter(
        self,
        db: Session,
        *,
        start: datetime,
        end: datetime,
        period: str,
        type: Optional[IaasType] = None,
        iaas: Optional[Iaas] = None,
        account: Optional[Account] = None,
    ) -> pd.DataFrame:
        query = (
            select(CloudMetric)
            .join(Account)
            .join(Iaas)
            .where(CloudMetric.time >= start)
            .where(CloudMetric.time < end)
        )
        if account:
            query = query.where(CloudMetric.account_id == account.id)
        if iaas:
            query = query.where(Account.iaas_id == iaas.id)
        if type:
            query = query.where(Iaas.type == type)
        metrics: List[CloudMetric] = (await db.execute(query)).scalars().fetchall()
        if not metrics:
            return pd.DataFrame()
        df = pd.DataFrame(
            data=[
                {
                    "x": metric.time,
                    "y": metric.instances,
                    "type": metric.account.iaas.type.name,
                }
                for metric in metrics
            ],
        )

        return (
            df.groupby(["type", pd.Grouper(key="x", freq=period)]).sum().reset_index()
        )


metric = MetricService()
