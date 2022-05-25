from typing import (
    Tuple,
    TypeVar,
    Generic,
    Optional,
    Type,
    Union,
    get_args,
    List,
    Dict,
    Any,
)

from fastapi import Depends
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.sql import Select
from sqlalchemy.orm import with_polymorphic
from sqlalchemy.ext.asyncio import AsyncSession as Session

from app.database.base import Base
from app.database.user import User
from app.model.common import SearchQueryBase
from app.api.core import get_db, get_current_user

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
FilterSchemaType = TypeVar("FilterSchemaType", bound=BaseModel)


class ServiceBase:
    db: Session
    user: Optional[User]

    def __init__(
        self, db: Session = Depends(get_db), user: User = Depends(get_current_user)
    ):
        self.db = db
        self.user = user


class CrudBase(
    ServiceBase,
    Generic[ModelType, CreateSchemaType, UpdateSchemaType, FilterSchemaType],
):
    model: Type[ModelType]

    # Bit of a hack to get the class instance of ModelType
    def __init_subclass__(cls) -> None:
        cls.model = get_args(cls.__orig_bases__[0])[0]  # type: ignore

    @property
    def query(self) -> Select:
        return select(with_polymorphic(self.model, "*"))

    async def get_all(self) -> List[ModelType]:
        return (await self.db.scalars(self.query)).all()

    async def get(self, *, id: int) -> Optional[ModelType]:
        return await self.db.scalar(self.query.where(self.model.id == id))

    async def get_by_name(self, *, name: str) -> Optional[ModelType]:
        if not hasattr(self.model, "name"):
            raise HTTPException(status_code=500, detail="Model does not have a name")
        return await self.db.scalar(self.query.where(self.model.name == name))

    async def create(
        self,
        *,
        data: Union[CreateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        data = data if isinstance(data, dict) else data.dict(exclude_unset=True)
        obj = self.model(**data)
        self.db.add(obj)
        await self.db.commit()
        return obj

    async def update(
        self,
        *,
        obj: ModelType,
        data: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        data = data if isinstance(data, dict) else data.dict(exclude_unset=True)
        for k, v in data.items():
            setattr(obj, k, v)
        await self.db.commit()
        return obj

    async def delete(self, *, obj: ModelType) -> None:
        self.db.delete(obj)
        await self.db.commit()

    async def _paginate(
        self,
        *,
        query: Select,
        pagination: SearchQueryBase,
    ) -> Tuple[List[ModelType], int]:
        offset = (pagination.page - 1) * pagination.per_page if pagination.page else 0
        total = await self.db.scalar(
            select([func.count()]).select_from(query.subquery())
        )
        if pagination.sort and hasattr(self.model, pagination.sort):
            attr = getattr(self.model, pagination.sort)
            query = query.order_by(
                attr.desc() if pagination.order == "desc" else attr.asc()
            )
        query = query.offset(offset).limit(pagination.per_page)
        print(query)
        return (await self.db.scalars(query)).all(), total

    async def search(
        self,
        *,
        query: Optional[Select] = None,
        filter: Optional[Union[FilterSchemaType, Dict[str, Any]]] = None,
        exclude: Optional[List[int]] = None,
        pagination: SearchQueryBase = SearchQueryBase(),
    ) -> Tuple[List[ModelType], int]:
        query = query or self.query
        if filter:
            filter = (
                filter if isinstance(filter, dict) else filter.dict(exclude_unset=True)
            )
            for k, v in (
                (k, v)
                for k, v in filter.items()
                if hasattr(self.model, k) and v is not None
            ):
                query = (
                    query.where(getattr(self.model, k).ilike(f"%{v}%"))
                    if isinstance(v, str)
                    else query.where(getattr(self.model, k) == v)
                )
        if exclude:
            query = query.where(~self.model.id.in_(exclude))
        return await self._paginate(query=query, pagination=pagination)
