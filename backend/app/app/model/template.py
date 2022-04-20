from typing import Optional

from pydantic import BaseModel, conlist


class TemplateFilter(BaseModel):
    name: Optional[str] = None


class CreateTemplate(BaseModel):
    name: str
    description: str
    order: conlist(int, unique_items=True)


class UpdateTemplate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    order: Optional[conlist(int, unique_items=True)] = None


class Template(BaseModel):
    id: int
    name: str
    description: str
    order: conlist(int, unique_items=True)

    class Config:
        orm_mode = True
