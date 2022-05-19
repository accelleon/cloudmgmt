from typing import TYPE_CHECKING, List, Generic, Optional, Any

from datetime import datetime

from pydantic import BaseModel
from pydantic.generics import GenericModel

from ..common import Model

if TYPE_CHECKING:
    from .cf import CloudFoundry
    from ..region import Region


class Metadata(BaseModel):
    guid: str
    url: str
    created_at: datetime
    updated_at: datetime
    updated_by: Optional[str]


class BaseResource(GenericModel, Generic[Model]):
    parent: Any
    region: Any
    me: Model

    @classmethod
    def from_model(cls, model: Model, parent: "CloudFoundry", region: "Region") -> "BaseResource[Model]":
        return cls(parent=parent, me=model, region=region)

    @classmethod
    def map_model(cls, models: List[Model], parent: "CloudFoundry", region: "Region") -> List["BaseResource[Model]"]:
        return [cls.from_model(model, parent, region) for model in models]
