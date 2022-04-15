from typing import TYPE_CHECKING, Union, Optional, Tuple, List

from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import Session, relationship, Query

from .base import Base, CRUDBase
from .iaas import Iaas  # noqa
from app.model.account import AccountFilter, CreateAccount, UpdateAccount
from pycloud import CloudFactory

if TYPE_CHECKING:
    from .billing import Billing  # noqa


class Account(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True, nullable=False)
    iaas_id = Column(Integer, ForeignKey("iaas.id"), nullable=False)
    data = Column(JSON, nullable=False)

    iaas = relationship("Iaas", back_populates="accounts")
    bills = relationship("Billing", back_populates="account")

    def __repr__(self):
        return f"Account(id={self.id!r}, name={self.name!r}, iaas_id={self.iaas_id!r}, data={self.data!r})"


class AccountCRUD(CRUDBase[Account, CreateAccount, UpdateAccount, AccountFilter]):
    def create(self, db: Session, *, obj_in: CreateAccount) -> Account:
        # Get the Iaas object from its name
        dbIaas = db.query(Iaas).filter(Iaas.name == obj_in.iaas).first()
        if not dbIaas:
            raise ValueError(f"Iaas {obj_in.iaas} not found")

        db_obj = Account(
            name=obj_in.name,
            data=obj_in.data,
            iaas=dbIaas,
        )  # type: ignore
        # This'll chuck a ValidationException if the data is invalid
        CloudFactory.validate_client(dbIaas.name, obj_in.data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Account, obj_in: UpdateAccount) -> Account:
        if obj_in.data is not None and db_obj.data != obj_in.data:
            # If we updated any portion of the data, validate it
            for k, v in db_obj.data.items():  # type: ignore
                if k not in obj_in.data:
                    obj_in.data[k] = v

            CloudFactory.validate_client(db_obj.iaas.name, obj_in.data)

        return super().update(db, db_obj=db_obj, obj_in=obj_in)

    def filter(
        self,
        db: Session,
        *,
        query: Optional[Query] = None,
        filter: Optional[AccountFilter] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
        order: Optional[str] = "asc",
        exclude: Optional[List[int]] = None,
    ) -> Tuple[List[Account], int]:
        if filter and filter.iaas:
            query = db.query(Account).join(Iaas).filter(Iaas.name == filter.iaas)
            filter.iaas = None
        return super().filter(
            db,
            query=query,
            filter=filter,
            offset=offset,
            limit=limit,
            sort=sort,
            order=order,
            exclude=exclude,
        )

    def get_by_name(self, db: Session, *, name: str, iaas: str) -> Union[Account, None]:
        return (
            db.query(Account)
            .join(Iaas)
            .filter(Account.name == name, Iaas.name == iaas)
            .first()
        )


account = AccountCRUD(Account)
