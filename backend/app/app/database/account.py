from typing import Union, Dict, Any, Optional

from sqlalchemy import Boolean, Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import Session, relationship

from .base import Base, CRUDBase
from .iaas import Iaas  # noqa
from app.model.account import AccountFilter, CreateAccount, UpdateAccount
from app.model.iaas import Iaas as IaasModel


class Account(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True, nullable=False)
    iaas_id = Column(Integer, ForeignKey("iaas.id"), nullable=False)
    data = Column(JSON, nullable=False)

    iaas = relationship("Iaas", back_populates="accounts")

    def __repr__(self):
        return (
            f"Account(id={self.id!r}, name={self.name!r}, iaas_id={self.iaas_id!r}, data={self.data!r})"
        )


class AccountCRUD(CRUDBase[Account, CreateAccount, UpdateAccount, AccountFilter]):
    def create(self, db: Session, *, obj_in: CreateAccount) -> Account:
        # Convert obj_in to a dict
        obj_in_data = (
            obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)
        )

        # Get the Iaas object from its name
        dbIaas = db.query(Iaas).filter(Iaas.name == obj_in.iaas).first()
        if not dbIaas:
            raise ValueError(f"Iaas {obj_in.iaas} not found")

        iaas = IaasModel.from_orm(dbIaas)
        for option in iaas.parameters:
            if option.name not in obj_in_data:
                raise ValueError(f"Missing option {option.name}")
            if option.type != type(obj_in_data[option.name]).__name__:
                raise ValueError(
                    f"Option {option.name} has type {option.type} but {type(obj_in_data[option.name]).__name__} was given"
                )

        db_obj = Account(
            name=obj_in.name,
            data=obj_in.data,
            iaas=dbIaas,
        )  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


account = AccountCRUD(Account)
