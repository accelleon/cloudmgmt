from typing import Optional

from pydantic import BaseModel


class GroupBase(BaseModel):
    id: str
    name: str


class GroupMember(BaseModel):
    group_id: int
    user_id: int
