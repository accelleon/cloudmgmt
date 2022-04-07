from sqlalchemy.orm import Session

from app import database
from app.model.iaas import Iaas, CreateIaas, IaasType, IaasOption
from app.model.account import Account, CreateAccount, UpdateAccount


def test_create_delete_account(
    db: Session,
) -> None:
    options = [
        IaasOption(name="name", type='str'),
    ]
    iaas_in = CreateIaas(name="test3", type=IaasType.PAAS, parameters=options)
    iaas = database.iaas.create(db, obj_in=iaas_in)

    data = {
        "name": "test",
    }

    account_in = CreateAccount(
        name="test",
        iaas="test3",
        data=data,
    )
    account = database.account.create(db, obj_in=account_in)
    assert account.name == "test"
    assert account.iaas_id == iaas.id
    assert account.data == data

    database.account.delete(db, id=account.id)
    assert database.account.get(db, id=account.id) is None

    database.iaas.delete(db, id=iaas.id)
