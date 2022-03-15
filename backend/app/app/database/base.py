from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

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

# Base class to derive CRUD implementations of DB items from
class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(
        self,
        db: Session,
        id: int
    ) -> Optional[ModelType]:
        return db.get(ModelType, id)

    def get_multi(
        self,
        db: Session,
        *, # Skip unnamed parameters
        offset: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(
        self,
        db: Session,
        *, # Skip unnamed parameters
        obj_in: CreateSchemaType
    ) -> ModelType:
        # Convert obj_in to a dict and initialize a ModelType with it
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in)
        # Push to DB
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *, # Skip unnamed parameters
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        # Convert the object we're updating to a dict
        obj_data = jsonable_encoder(db_obj)
        # Convert obj_in to a dict if it isn't already
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)
        # Run through the dict, setting the appropriate values for db_obj
        for k,v in obj_data.items():
            if key in update_data:
                setattr(db_obj, key, v)
        #TODO: Evaluate the possibility of removing this line `if db_obj in session.dirty`
        db.update(ModelType).where(self.id == db_obj.id).values(**update_data)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(
        self,
        db: Session,
        *, # Skip unnamed parameters
        id: int
    ) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj