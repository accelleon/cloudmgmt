from typing import TYPE_CHECKING, Optional, List, Dict

from sqlalchemy import select, Column, Integer, String, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession as Session

from .base import Base, CRUDBase
from app.model.iaas import IaasDesc, IaasFilter, IaasType

if TYPE_CHECKING:
    from app.database.account import Account  # noqa


class Iaas(Base):
    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, index=True, unique=True, nullable=False)
    type: IaasType = Column(Enum(IaasType), nullable=False)
    params: Dict[str, str] = Column(JSON, nullable=False)

    accounts: List['Account'] = relationship("Account", back_populates="iaas", lazy="selectin")

    def __repr__(self):
        return f"Iaas(id={self.id!r}, type={self.type!r}, name={self.name!r}, parameters={self.params!r})"


class CRUDIaas(CRUDBase[Iaas, IaasDesc, IaasDesc, IaasFilter]):
    async def get_by_name(self, db: Session, *, name: str) -> Optional[Iaas]:
        return (
            (await db.execute(select(Iaas).where(Iaas.name == name))).scalars().first()
        )


iaas = CRUDIaas(Iaas)
