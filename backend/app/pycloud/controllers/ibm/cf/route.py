from typing import Optional
from pydantic import BaseModel


class RouteDomain(BaseModel):
    guid: str
    name: str


class Route(BaseModel):
    guid: str
    host: str
    port: Optional[int]
    path: str
    domain: RouteDomain
