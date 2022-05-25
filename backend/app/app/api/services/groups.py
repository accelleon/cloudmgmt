from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.sql import Select
from sqlalchemy.orm import selectinload

from app.database import Group, Account, Iaas
from app.model import CreateGroup, UpdateGroup, FilterGroup
from app.api.core.security import Permission
from .base import CrudBase


class GroupService(CrudBase[Group, CreateGroup, UpdateGroup, FilterGroup]):
    @property
    def query(self) -> Select:
        return select(self.model).options(selectinload(Group.accounts))
