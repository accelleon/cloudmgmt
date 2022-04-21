from datetime import datetime
from typing import Union, Optional, Tuple, List, Dict

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    Float,
    asc,
    desc,
    select,
)
from sqlalchemy.sql import Select
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession as Session

from .base import Base, CRUDBase
from .account import Account  # noqa
from .iaas import Iaas
from app.model.billing import (
    BillingPeriodFilter,
    UpdateBillingPeriod,
    CreateBillingPeriod,
)

from pycloud.utils import current_month_date_range


class Billing(Base):
    id: int = Column(Integer, primary_key=True, index=True)
    account_id: int = Column(Integer, ForeignKey("account.id"), nullable=False)
    start_date: datetime = Column(DateTime(timezone=True), nullable=False)
    end_date: datetime = Column(DateTime(timezone=True), nullable=False)
    total: float = Column(Float, nullable=False)
    balance: float = Column(Float, nullable=False)

    account: Account = relationship("Account", lazy="selectin")

    def __repr__(self):
        return f"Billing(id={self.id!r}, account_id={self.account_id!r}, start_date={self.start_date!r}, end_date={self.end_date!r}, total={self.total!r}, balance={self.balance!r})"  # noqa


class BillingCRUD(
    CRUDBase[Billing, CreateBillingPeriod, UpdateBillingPeriod, BillingPeriodFilter]
):
    async def filter(
        self,
        db: Session,
        *,
        query: Optional[Select] = None,
        filter: Optional[Union[BillingPeriodFilter, Dict]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
        order: Optional[str] = "asc",
        exclude: Optional[List[int]] = None,
    ) -> Tuple[List[Billing], int]:
        query = query if query is not None else select(Billing).join(Account).join(Iaas)
        if filter:
            filter = (
                BillingPeriodFilter(**filter) if isinstance(filter, dict) else filter
            )
            if filter.account and not filter.iaas:
                raise ValueError("Must specify iaas when filtering by account")
            if filter.iaas:
                query = query.where(Iaas.name == filter.iaas)
            if filter.account:
                query = query.where(Account.name == filter.account)
            if filter.start_date:
                query = query.where(Billing.end_date >= filter.start_date)
            if filter.end_date:
                query = query.where(Billing.end_date < filter.end_date)
        op = asc if order == "asc" else desc
        if sort == "iaas":
            query = query.order_by(op(Iaas.name))
            sort = None
        if sort == "account":
            query = query.order_by(op(Account.name))
            sort = None
        return await super().filter(
            db,
            query=query,
            filter=None,
            offset=offset,
            limit=limit,
            sort=sort,
            order=order,
            exclude=exclude,
        )

    async def get_by_period(
        self,
        db: Session,
        *,
        account_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> Optional[Billing]:
        return (
            (
                await db.execute(
                    select(Billing).where(
                        Billing.account_id == account_id,
                        Billing.start_date == start_date,
                        Billing.end_date == end_date,
                    )
                )
            )
            .scalars()
            .first()
        )

    async def get_cur_period(
        self,
        db: Session,
    ) -> List[Billing]:
        start, end = current_month_date_range()
        return (
            (
                await db.execute(
                    select(Billing).where(
                        Billing.end_date >= start,
                        Billing.end_date <= end,
                    )
                )
            )
            .scalars()
            .all()
        )


billing = BillingCRUD(Billing)
