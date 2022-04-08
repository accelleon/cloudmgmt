from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, Integer, String, ARRAY, Enum
from sqlalchemy.orm import Session, relationship

from .base import Base, CRUDBase
from app.model.iaas import IaasDesc, IaasType

if TYPE_CHECKING:
    from app.database.account import Account  # noqa


class Iaas(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True, nullable=False)
    type = Column(Enum(IaasType), nullable=False)
    params = Column(ARRAY(String), nullable=False)

    accounts = relationship("Account", back_populates="iaas")

    def __repr__(self):
        return f"Iaas(id={self.id!r}, type={self.type!r}, name={self.name!r}, parameters={self.params!r})"


class CRUDIaas(CRUDBase[Iaas, IaasDesc, IaasDesc, IaasDesc]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Iaas]:
        return db.query(Iaas).filter(Iaas.name == name).first()


iaas = CRUDIaas(Iaas)
