from typing import List, Union, Dict, Any, Optional, Tuple

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.sql import Select

from app.core.security import (
    hash_password,
    create_secret,
)
from app.database import User
from app.model import CreateUser, UpdateUser, UserFilter, SearchQueryBase
from .base import CrudBase


class UserService(CrudBase[User, CreateUser, UpdateUser, UserFilter]):
    async def create(self, *, data: Union[CreateUser, Dict[str, Any]]) -> User:
        data.password = hash_password(data.password)
        return await super().create(data=data)

    async def update(
        self, *, obj: User, data: Union[UpdateUser, Dict[str, Any]]
    ) -> User:
        data = data if isinstance(data, dict) else data.dict(exclude_unset=True)

        if "password" in data:
            data["password"] = hash_password(data["password"])

        if "twofa_enabled" in data and data["twofa_enabled"] != obj.twofa_enabled:
            if not obj.twofa_secret:
                data["twofa_secret"] = create_secret()
                data["twofa_enabled"] = False
            if not data["twofa_enabled"]:
                data["twofa_secret"] = None

        return await super().update(obj=obj, data=data)

    async def delete(self, *, obj: User) -> None:
        await super().delete(obj=obj)

    async def search(
        self,
        *,
        query: Optional[Select] = None,
        filter: Optional[Union[UserFilter, Dict[str, Any]]] = None,
        exclude: Optional[List[int]] = None,
        pagination: SearchQueryBase = SearchQueryBase(),
    ) -> Tuple[List[User], int]:
        exclude = (exclude or []) + [self.user.id]
        return await super().search(
            query=query,
            filter=filter,
            exclude=exclude,
            pagination=pagination,
        )

    async def get_by_name(self, name: str) -> User:
        return await self.db.scalar(select(User).where(User.username == name))
