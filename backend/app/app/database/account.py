from typing import TYPE_CHECKING, Union, Optional, Tuple, List, Dict

from sqlalchemy import select, Column, Integer, String, JSON, ForeignKey
from sqlalchemy.sql import Select
from sqlalchemy.orm import relationship, joinedload, Mapped
from sqlalchemy.ext.asyncio import AsyncSession as Session

from .base import Base, CRUDBase
from .iaas import Iaas  # noqa
from app.model.account import AccountFilter, CreateAccount, UpdateAccount
from pycloud import CloudFactory

if TYPE_CHECKING:
    from .billing import Billing  # noqa


class Account(Base):
    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, index=True, unique=True, nullable=False)
    iaas_id: int = Column(Integer, ForeignKey("iaas.id"), nullable=False)
    currency: str = Column(String(length=3), nullable=False)
    data: JSON = Column(JSON, nullable=False)

    iaas = relationship("Iaas", lazy="selectin")
    bills = relationship("Billing", back_populates="account", lazy="noload")

    def __repr__(self):
        return f"Account(id={self.id!r}, name={self.name!r}, iaas_id={self.iaas_id!r}, data={self.data!r})"


class AccountCRUD(CRUDBase[Account, CreateAccount, UpdateAccount, AccountFilter]):
    async def get(self, db: Session, id: int) -> Optional[Account]:
        return (
            (await db.execute(select(Account).where(Account.id == id)))
            .scalars()
            .first()
        )

    async def create(self, db: Session, *, obj_in: CreateAccount) -> Account:
        # Get the Iaas object from its name
        dbIaas = (
            (await db.execute(select(Iaas).where(Iaas.name == obj_in.iaas)))
            .scalars()
            .first()
        )
        if not dbIaas:
            raise ValueError(f"Iaas {obj_in.iaas} not found")

        db_obj = Account(
            name=obj_in.name,
            data=obj_in.data,
            iaas=dbIaas,
        )  # type: ignore
        # This'll chuck a ValidationException if the data is invalid
        db_obj.currency = CloudFactory.get_client(dbIaas.name, obj_in.data).currency()
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: Session,
        *,
        db_obj: Account,
        obj_in: Union[UpdateAccount, Dict[str, str]],
    ) -> Account:
        obj_in = UpdateAccount(**obj_in) if isinstance(obj_in, dict) else obj_in
        if obj_in.data is not None and db_obj.data != obj_in.data:
            # If we updated any portion of the data, validate it
            for k, v in db_obj.data.items():  # type: ignore
                if k not in obj_in.data:
                    obj_in.data[k] = v

            CloudFactory.get_client(db_obj.iaas.name, obj_in.data)

        return await super().update(db, db_obj=db_obj, obj_in=obj_in)

    async def filter(
        self,
        db: Session,
        *,
        query: Optional[Select] = None,
        filter: Optional[Union[AccountFilter, Dict]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
        order: Optional[str] = "asc",
        exclude: Optional[List[int]] = None,
    ) -> Tuple[List[Account], int]:
        filter = AccountFilter(**filter) if isinstance(filter, dict) else filter
        query = select(Account)
        if filter and filter.iaas:
            query = query.where(Iaas.name == filter.iaas)

            filter.iaas = None
        return await super().filter(
            db,
            query=query,
            filter=filter,
            offset=offset,
            limit=limit,
            sort=sort,
            order=order,
            exclude=exclude,
        )

    async def get_by_name(
        self, db: Session, *, name: str, iaas: str
    ) -> Union[Account, None]:
        return (
            (
                await db.execute(
                    select(Account)
                    .join(Iaas)
                    .where(Iaas.name == iaas, Account.name == name)
                )
            )
            .scalars()
            .first()
        )


account = AccountCRUD(Account)
