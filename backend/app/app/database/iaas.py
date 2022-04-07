from typing import Union, Dict, Any, Optional
from pydantic import ValidationError

from sqlalchemy import Boolean, Column, Integer, String, JSON, ForeignKey, Enum
from sqlalchemy.orm import Session, relationship

from .base import Base, CRUDBase
from app.model.iaas import CreateIaas, IaasOption, IaasType


class Iaas(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True, nullable=False)
    type = Column(Enum(IaasType), nullable=False)
    parameters = Column(JSON, nullable=False)

    accounts = relationship("Account", back_populates="iaas")

    def __repr__(self):
        return f"Iaas(id={self.id!r}, type={self.type!r}, name={self.name!r}, parameters={self.parameters!r})"

class CRUDIaas(CRUDBase[Iaas, CreateIaas, CreateIaas, CreateIaas]):
    pass


iaas = CRUDIaas(Iaas)
