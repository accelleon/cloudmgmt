from typing import TYPE_CHECKING, List, Optional, TypeVar, Generic, Any
from pydantic import BaseModel
from pydantic.generics import GenericModel

if TYPE_CHECKING:
    from .ibm import IBMApi

Model = TypeVar("Model", bound=BaseModel)


class Pagination(GenericModel, Generic[Model]):
    total_results: int
    total_pages: int
    prev_url: Optional[str]
    next_url: Optional[str]
    resources: List[Model]


class BaseResource(GenericModel, Generic[Model]):
    parent: Any
    me: Model

    @classmethod
    def from_model(cls, model: Model, parent: "IBMApi") -> "BaseResource[Model]":
        return cls(parent=parent, me=model)

    @classmethod
    def map_model(cls, models: List[Model], parent: "IBMApi") -> List["BaseResource[Model]"]:
        return [cls.from_model(model, parent) for model in models]
