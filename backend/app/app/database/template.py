from typing import List, Union, Dict, Any, Optional

from sqlalchemy import delete, insert, select, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.event import listens_for
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession as Session

from app.database.base import Base, CRUDBase
from app.database import Account
from app.model import CreateTemplate, UpdateTemplate, TemplateFilter


class TemplateOrder(Base):
    __tablename__ = "template_order"

    id: int = Column(Integer, primary_key=True)
    template_id: int = Column(Integer, ForeignKey("template.id"), nullable=False, index=True)
    account_id: int = Column(Integer, ForeignKey("account.id"), nullable=False)
    # include: bool = Column(Boolean, nullable=False, index=True)
    sort_order: int = Column(Integer, nullable=False)

    account: Account = relationship("Account", lazy="selectin")

    def __repr__(self):
        return f"TemplateOrder(id={self.id!r}, name={self.name!r}, description={self.description!r}, price={self.price!r}, is_active={self.is_active!r})"


class Template(Base):
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String, nullable=False, index=True, unique=True)
    description: str = Column(String, nullable=False)

    orders: List[TemplateOrder] = relationship("TemplateOrder", lazy="selectin", cascade="all, delete-orphan")

    def __repr__(self):
        return f"Template(id={self.id!r}, name={self.name!r}, description={self.description!r})"


class CRUDTemplate(CRUDBase[Template, CreateTemplate, UpdateTemplate, TemplateFilter]):
    # Class overrides
    async def update(
        self,
        db: Session,
        *,  # Skip unnamed parameters
        db_obj: Template,
        obj_in: Union[UpdateTemplate, Dict[str, Any]],
    ) -> Template:
        update_date = (
            obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)
        )

        # Are we updating the ordering?
        # TODO: This is a bit of a hack, but it works for now.
        if "order" in update_date:
            await db.execute(
                delete(TemplateOrder).where(TemplateOrder.template_id == db_obj.id)
            )
            await db.refresh(db_obj)
            for order, account_id in enumerate(update_date["order"]):
                obj = TemplateOrder(template_id=db_obj.id, account_id=account_id, sort_order=order)
                db.add(obj)
            del update_date["order"]

        return await super().update(db, db_obj=db_obj, obj_in=update_date)

    async def create(
        self,
        db: Session,
        *,  # Skip unnamed parameters
        obj_in: Union[CreateTemplate, Dict[str, Any]],
    ) -> Template:
        obj_in = obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)

        obj = Template(name=obj_in["name"], description=obj_in["description"])
        db.add(obj)
        await db.commit()
        await db.refresh(obj)

        for order, account_id in enumerate(obj_in["order"]):
            tmpobj = TemplateOrder(template_id=obj.id, account_id=account_id, sort_order=order)
            db.add(tmpobj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def get_by_name(self, db: Session, *, name: str) -> Optional[Template]:
        return (await db.execute(
            select(Template).where(Template.name == name)
        )).scalars().first()


template = CRUDTemplate(Template)


# Automatically append new accounts to existing templates
@listens_for(Account, "after_insert")
async def _after_insert(mapper, connection: AsyncConnection, target: Account):
    templates = (await connection.execute(select(Template))).scalars().all()
    for template in templates:
        await connection.execute(
            insert(TemplateOrder).values(template_id=template.id, account_id=target.id, sort_order=len(template.orders))
        )
    connection.commit()
