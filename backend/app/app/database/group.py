from typing import TYPE_CHECKING, List

from sqlalchemy import (
    Column,
    Integer,
    String,
)
from sqlalchemy.orm import relationship


from .base import Base

if TYPE_CHECKING:
    from .account import Account


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    accounts: List["Account"] = relationship(
        "Account", lazy="noload", back_populates="group"
    )

    def __repr__(self):
        return f"<Group {self.name}>"
