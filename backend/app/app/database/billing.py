from datetime import datetime
from typing import Union, Optional, Tuple, List, Dict

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    Float,
    String,
    asc,
    desc,
    select,
)
from sqlalchemy.sql import Select
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession as Session
from dateutil.relativedelta import relativedelta

from .base import Base, CRUDBase
from .account import Account  # noqa
from .iaas import Iaas
from app.model.billing import (
    BillingPeriodFilter,
    UpdateBillingPeriod,
    CreateBillingPeriod,
)


class BillingPeriod(Base):
    __tablename__ = "billing_period"  # type: ignore
    id: int = Column(Integer, primary_key=True, index=True)
    period: str = Column(String(9), index=True, unique=True)

    billing: List["Billing"] = relationship(
        "Billing", back_populates="period", lazy="selectin"
    )


class Billing(Base):
    id: int = Column(Integer, primary_key=True, index=True)
    account_id: int = Column(Integer, ForeignKey("account.id"), nullable=False)
    period_id: int = Column(Integer, ForeignKey("billing_period.id"), nullable=False)
    start_date: datetime = Column(DateTime(timezone=True), nullable=False)
    end_date: datetime = Column(DateTime(timezone=True), nullable=False)
    total: float = Column(Float, nullable=False)
    balance: Optional[float] = Column(Float, nullable=False)

    period: BillingPeriod = relationship("BillingPeriod", back_populates="billing")
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
        query = query if query is not None else select(Billing).join(BillingPeriod).join(Account).join(Iaas)
        if filter:
            filter = (
                BillingPeriodFilter(**filter) if isinstance(filter, dict) else filter
            )
            if filter.period:
                query = query.where(BillingPeriod.period == filter.period)
            if filter.account and not filter.iaas:
                raise ValueError("Must specify iaas when filtering by account")
            if filter.iaas:
                query = query.where(Iaas.name == filter.iaas)
            if filter.account:
                query = query.where(Account.name == filter.account)
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

    async def create(
        self,
        db: Session,
        *,
        obj_in: CreateBillingPeriod,
    ) -> Billing:
        # Cloud providers have end date as exclusive normally subtract 1 day
        period = (obj_in.end_date - relativedelta(days=1)).strftime("%Y-%m")
        billing_period = await self.get_period(db, period=period)
        if not billing_period:
            billing_period = BillingPeriod(period=period)
            db.add(billing_period)
            await db.commit()
            await db.refresh(billing_period)

        billing = Billing(
            account_id=obj_in.account_id,
            period_id=billing_period.id,
            start_date=obj_in.start_date,
            end_date=obj_in.end_date,
            total=obj_in.total,
            balance=obj_in.balance,
        )
        db.add(billing)
        await db.commit()
        await db.refresh(billing)
        return billing

    async def get_period(
        self,
        db: Session,
        *,
        period: str,
    ) -> Optional[BillingPeriod]:
        return (
            (
                await db.execute(
                    select(BillingPeriod).where(BillingPeriod.period == period)
                )
            )
            .scalars()
            .first()
        )

    async def get_periods(
        self,
        db: Session,
    ) -> List[str]:
        return (
            (
                await db.execute(
                    select(BillingPeriod.period).order_by(desc(BillingPeriod.period))
                )
            )
            .scalars()
            .all()
        )

    async def get_account_period(
        self,
        db: Session,
        *,
        account_id: int,
        period: str,
    ) -> Optional[Billing]:
        return (
            (
                await db.execute(
                    select(BillingPeriod.billing).where(
                        BillingPeriod.period == period,
                        Billing.account_id == account_id,
                    )
                )
            )
            .scalars()
            .first()
        )

    async def get_billing_period(
        self,
        db: Session,
        *,
        period: str,
    ) -> List[Billing]:
        resp = (
            (
                await db.execute(
                    select(BillingPeriod).where(BillingPeriod.period == period)
                )
            )
            .scalars()
            .first()
        )
        return resp.billing if resp else None


billing = BillingCRUD(Billing)
