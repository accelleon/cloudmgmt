from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import Session, relationship

from .base import Base, CRUDBase
from .iaas import Iaas  # noqa
from app.model.account import AccountFilter, CreateAccount, UpdateAccount
from app.cloud import CloudFactory


class Account(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True, nullable=False)
    iaas_id = Column(Integer, ForeignKey("iaas.id"), nullable=False)
    data = Column(JSON, nullable=False)

    iaas = relationship("Iaas", back_populates="accounts")

    def __repr__(self):
        return f"Account(id={self.id!r}, name={self.name!r}, iaas_id={self.iaas_id!r}, data={self.data!r})"


class AccountCRUD(CRUDBase[Account, CreateAccount, UpdateAccount, AccountFilter]):
    def create(self, db: Session, *, obj_in: CreateAccount) -> Account:
        # Get the Iaas object from its name
        dbIaas = db.query(Iaas).filter(Iaas.name == obj_in.iaas).first()
        if not dbIaas:
            raise ValueError(f"Iaas {obj_in.iaas} not found")

        db_obj = Account(
            name=obj_in.name,
            data=obj_in.data,
            iaas=dbIaas,
        )  # type: ignore
        CloudFactory.get_client(db_obj)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


account = AccountCRUD(Account)
