from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union, Tuple

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import as_declarative, declared_attr


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

    def get(self, db: Session, id: Optional[int]) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self,
        db: Session,
    ) -> List[ModelType]:
        return db.query(self.model).all()

    def filter(
        self,
        db: Session,
        *,
        filter: Optional[Union[FilterSchemaType, Dict[str, Any]]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Optional[str] = None
    ) -> Tuple[List[ModelType], int]:
        query = db.query(self.model)
        if filter:
            filter_in = (
                filter if isinstance(filter, dict) else filter.dict(exclude_unset=True)
            )
            for k, v in filter_in.items():
                if hasattr(self.model, k) and v:
                    query = query.filter(getattr(self.model, k) == v)
        total = query.count()
        if sort and hasattr(self.model, sort):
            query = query.order_by(sort)
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        return query.all(), total

    def create(
        self, db: Session, *, obj_in: CreateSchemaType  # Skip unnamed parameters
    ) -> ModelType:
        # Convert obj_in to a dict and initialize a ModelType with it
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        # Push to DB
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,  # Skip unnamed parameters
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        # Convert the object we're updating to a dict
        obj_data = jsonable_encoder(db_obj)
        # Convert obj_in to a dict if it isn't already
        update_data = (
            obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)
        )
        # Run through the dict, setting the appropriate values for db_obj
        for k in obj_data:
            if k in update_data:
                setattr(db_obj, k, update_data[k])
        # TODO: Evaluate the possibility of removing this line `if db_obj in session.dirty`
        # db.update(ModelType).where(self.id == db_obj.id).values(**update_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(
        self, db: Session, *, id: int  # Skip unnamed parameters
    ) -> Optional[ModelType]:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj
