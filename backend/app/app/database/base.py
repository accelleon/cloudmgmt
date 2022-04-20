from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union, Tuple

from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.sql import Select
from sqlalchemy.orm import as_declarative, declared_attr
from sqlalchemy.ext.asyncio import AsyncSession as Session


# Base class to derive DB items from
@as_declarative()
class Base:
    id: Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


# ModelType must derive from Base
ModelType = TypeVar("ModelType", bound=Base)
# These must derive from BaseModel
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
FilterSchemaType = TypeVar("FilterSchemaType", bound=BaseModel)


# Base class to derive CRUD implementations of DB items from
class CRUDBase(
    Generic[ModelType, CreateSchemaType, UpdateSchemaType, FilterSchemaType]
):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    async def get(self, db: Session, id: int) -> Optional[ModelType]:
        return (
            (await db.execute(select(self.model).where(self.model.id == id)))
            .scalars()
            .first()
        )

    async def get_multi(
        self,
        db: Session,
    ) -> List[ModelType]:
        return (await db.execute(select(self.model))).scalars().all()

    async def filter(
        self,
        db: Session,
        *,
        query: Optional[Select] = None,
        filter: Optional[Union[FilterSchemaType, Dict[str, Any]]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
        order: Optional[str] = "asc",
        exclude: Optional[List[int]] = None,
    ) -> Tuple[List[ModelType], int]:
        query = query if query is not None else select(self.model)
        if filter:
            filter_in = (
                filter if isinstance(filter, dict) else filter.dict(exclude_unset=True)
            )
            for k, v in filter_in.items():
                if hasattr(self.model, k) and v is not None:
                    if type(v) is str:
                        query = query.where(getattr(self.model, k).ilike(f"%{v}%"))
                    else:
                        query = query.where(getattr(self.model, k) == v)
        if exclude:
            query = query.where(~self.model.id.in_(exclude))
        subquery = query.subquery()
        total = await db.scalar(select(func.count()).select_from(subquery))
        if sort and hasattr(self.model, sort):
            attr = getattr(self.model, sort)
            query = query.order_by(attr.desc() if order == "desc" else attr.asc())
        query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        return (await db.execute(query)).scalars().all(), total

    async def create(
        self, db: Session, *, obj_in: CreateSchemaType  # Skip unnamed parameters
    ) -> ModelType:
        # Convert obj_in to a dict and initialize a ModelType with it
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data)  # type: ignore
        # Push to DB
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: Session,
        *,  # Skip unnamed parameters
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        # Convert obj_in to a dict if it isn't already
        update_data = (
            obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)
        )
        # Run through the dict, setting the appropriate values for db_obj
        for k in update_data:
            if hasattr(db_obj, k):
                setattr(db_obj, k, update_data[k])
        # TODO: Evaluate the possibility of removing this line `if db_obj in session.dirty`
        # db.update(ModelType).where(self.id == db_obj.id).values(**update_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: Session, *, id: int) -> None:
        obj = await self.get(db, id)
        await db.delete(obj)
        await db.commit()
