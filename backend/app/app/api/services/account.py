from typing import List, Union, Dict, Any, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.sql import Select
from sqlalchemy.orm import selectinload

from app.api.core import exception
from app.database import Account, Iaas, Group
from app.model import CreateAccount, UpdateAccount, AccountFilter, SearchQueryBase
from .base import CrudBase

from pycloud import CloudFactory


class AccountService(CrudBase[Account, CreateAccount, UpdateAccount, AccountFilter]):
    @property
    def query(self) -> Select:
        return select(self.model).options(
            selectinload(Account.iaas), selectinload(Account.group)
        )

    async def create(self, *, data: CreateAccount) -> Account:
        if not (
            iaas := await self.db.scalar(select(Iaas).where(Iaas.name == data.iaas))
        ):
            raise exception.InvalidParameter(f"Iaas {data.iaas} does not exist")
        if not (
            group := await self.db.scalar(select(Group).where(Group.name == data.group))
        ):
            raise exception.InvalidParameter(f"Group {data.group} does not exist")
        if await self.get_by_name(name=data.name):
            raise exception.Conflict(self.model, data.name)

        db_obj = Account(
            name=data.name,
            data=data.data,
            iaas=iaas,
            group=group,
        )
        db_obj.currency = CloudFactory.get_client(iaas.name, db_obj.data).currency()
        self.db.add(db_obj)
        await self.db.commit()
        return db_obj

    async def update(
        self, *, obj: Account, data: Union[UpdateAccount, Dict[str, Any]]
    ) -> Account:
        data = data if isinstance(data, dict) else data.dict(exclude_unset=True)
        if group_name := data.get("group"):
            if group := await self.db.scalar(
                select(Group).where(Group.name == group_name)
            ):
                data["group"] = group
            else:
                raise exception.InvalidParameter(
                    f"Group {data['group']} does not exist"
                )

        if "data" in data:
            for k, v in obj.data.items():  # type: ignore
                if k not in data["data"]:
                    data["data"][k] = v
            CloudFactory.get_client(obj.iaas.name, data["data"])

        return await super().update(obj=obj, data=data)

    async def search(
        self,
        *,
        query: Optional[Select] = None,
        filter: Optional[Union[AccountFilter, Dict[str, Any]]] = None,
        exclude: Optional[List[int]] = [],
        pagination: SearchQueryBase = SearchQueryBase(),
    ) -> Tuple[List[Account], int]:
        filter = filter if isinstance(filter, dict) else filter.dict(exclude_unset=True)
        query = query if query is not None else self.query
        if filter:
            if filter["iaas"]:
                query = query.where(Iaas.name == filter["iaas"])
                del filter["iaas"]
            if filter["type"]:
                query = query.where(Iaas.type == filter["type"])
                del filter["type"]
            if filter["group"]:
                query = query.where(Group.name == filter["group"])
                del filter["group"]
        return await super().search(
            query=query,
            filter=filter,
            exclude=exclude,
            pagination=pagination,
        )
