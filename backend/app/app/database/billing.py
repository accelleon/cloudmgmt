from typing import Union, Optional, Tuple, List, Dict

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Float, asc, desc
from sqlalchemy.orm import Session, relationship, Query

from .base import Base, CRUDBase
from .account import Account  # noqa
from .iaas import Iaas
from app.model.billing import (
    BillingPeriodFilter,
    UpdateBillingPeriod,
    CreateBillingPeriod,
)


class Billing(Base):
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("account.id"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    total = Column(Float, nullable=False)
    balance = Column(Float, nullable=False)

    account = relationship("Account", back_populates="bills")

    def __repr__(self):
        return f"Billing(id={self.id!r}, account_id={self.account_id!r}, start_date={self.start_date!r}, end_date={self.end_date!r}, total={self.total!r}, balance={self.balance!r})"


class BillingCRUD(
    CRUDBase[Billing, CreateBillingPeriod, UpdateBillingPeriod, BillingPeriodFilter]
):
    def filter(
        self,
        db: Session,
        *,
        query: Optional[Query] = None,
        filter: Optional[Union[BillingPeriodFilter, Dict]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
        order: Optional[str] = "asc",
        exclude: Optional[List[int]] = None,
    ) -> Tuple[List[Billing], int]:
        query = query if query is not None else db.query(Billing)
        if filter:
            filter = (
                BillingPeriodFilter(**filter) if isinstance(filter, dict) else filter
            )
            if filter.account and not filter.iaas:
                raise ValueError("Must specify iaas when filtering by account")
            if filter.iaas:
                query = query.join(Account).join(Iaas).filter(Iaas.name == filter.iaas)
            if filter.account:
                query = query.join(Account).filter(Account.name == filter.account)  # type: ignore
            if filter.start_date:
                query = query.filter(Billing.end_date >= filter.start_date)  # type: ignore
            if filter.end_date:
                query = query.filter(Billing.end_date < filter.end_date)  # type: ignore
        op = asc if order == "asc" else desc
        if sort == 'iaas':
            query = query.join(Account).join(Iaas).order_by(op(Iaas.name))
            sort = None
        if sort == 'account':
            query = query.join(Account).order_by(op(Account.name))
            sort = None
        return super().filter(
            db,
            query=query,
            filter=None,
            offset=offset,
            limit=limit,
            sort=sort,
            order=order,
            exclude=exclude,
        )


billing = BillingCRUD(Billing)
