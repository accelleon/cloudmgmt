from sqlalchemy.orm import Session

from app import database
from app.cloud import CloudFactory
from app.model.account import Account, CreateAccount, UpdateAccount


def test_create_delete_account(
    db: Session,
) -> None:
    pass
