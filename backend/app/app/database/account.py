from typing import TYPE_CHECKING, Union, Optional, Tuple, List, Dict
import traceback

from sqlalchemy import (
    select,
    Column,
    Integer,
    String,
    JSON,
    ForeignKey,
    Boolean,
)
from sqlalchemy.sql import Select
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession as Session

from .base import Base, CRUDBase
from .iaas import Iaas
from .group import Group
from app.model.account import AccountFilter, CreateAccount, UpdateAccount
from pycloud import CloudFactory, exc

if TYPE_CHECKING:
    from .billing import Billing  # noqa
    from .template import TemplateOrder  # noqa


class Account(Base):
    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, index=True, unique=True, nullable=False)
    iaas_id: int = Column(Integer, ForeignKey("iaas.id"), nullable=False)
    group_id: int = Column(Integer, ForeignKey("groups.id"), nullable=False)
    currency: str = Column(String(length=3), nullable=False)
    data: Dict[str, str] = Column(JSON, nullable=False)
    validated: bool = Column(Boolean, nullable=False, default=False)
    last_error: Optional[str] = Column(String, nullable=True)

    iaas: Iaas = relationship("Iaas", lazy="selectin")
    group: Group = relationship("Group", lazy="selectin")
    bills: List["Billing"] = relationship(
        "Billing", back_populates="account", lazy="noload", cascade="all, delete-orphan"
    )
    templateorder: List["TemplateOrder"] = relationship(
        "TemplateOrder",
        back_populates="account",
        lazy="noload",
        cascade="all, delete-orphan",
    )

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

        group = await db.scalar(select(Group).where(Group.name == obj_in.group))
        if not group:
            raise ValueError(f"Group {obj_in.group} not found")

        db_obj = Account(
            name=obj_in.name,
            data=obj_in.data,
            iaas=dbIaas,
            group=group,
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
        query = select(Account).join(Iaas)
        if filter:
            if filter.iaas:
                query = query.where(Iaas.name == filter.iaas)
                filter.iaas = None
            if filter.type:
                query = query.where(Iaas.type == filter.type)
                filter.type = None

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

    async def validate(self, db: Session, *, account: Account) -> Account:
        if account.validated:
            return account
        try:
            client = CloudFactory.get_client(account.iaas.name, account.data)
            await client.validate_account()
            account.validated = True
            account.last_error = None
        except exc.AuthorizationError as e:
            account.validated = False
            account.last_error = str(e)
        except Exception:
            # Some other error, don't modify anything
            print(traceback.format_exc())
            return account

        db.add(account)
        await db.commit()
        await db.refresh(account)
        return account


account = AccountCRUD(Account)
