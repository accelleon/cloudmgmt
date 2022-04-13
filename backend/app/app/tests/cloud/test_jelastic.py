from pydantic import ValidationError
import pytest
from sqlalchemy.orm import Session
from app.cloud.factory import CloudFactory

from app.model.account import Account
from app.model.iaas import Iaas
from app.database import iaas


def test_make_client(db: Session) -> None:
    iaasDb = iaas.get_by_name(db, name="Jelastic")
    account = Account(
        id=None,
        name="test",
        iaas=Iaas.from_orm(iaasDb),
        data={
            "endpoint": "https://jelastic.com",
            "api_key": "secret",
        },
    )
    CloudFactory.get_client(account)


def test_make_client_no_endpoint(db: Session) -> None:
    iaasDb = iaas.get_by_name(db, name="Jelastic")
    with pytest.raises(ValidationError):
        account = Account(
            id=None,
            name="test",
            iaas=Iaas.from_orm(iaasDb),
            data={
                "api_key": "secret",
            },
        )
        CloudFactory.get_client(account)
