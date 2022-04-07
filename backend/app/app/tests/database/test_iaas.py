from sqlalchemy.orm import Session

from app import database
from app.model.iaas import Iaas, CreateIaas, IaasType, IaasOption


def test_create_delete_iaas(db: Session) -> None:
    options = [
        IaasOption(name="name", type='str', secret=False),
    ]
    iaas_in = CreateIaas(name="test", type=IaasType.PAAS, parameters=options)
    iaas = database.iaas.create(db, obj_in=iaas_in)
    print(iaas)
    iaas2 = database.iaas.get(db, id=iaas.id)
    assert iaas2
    assert iaas2.name == "test"
    assert iaas2.type == IaasType.PAAS
    assert iaas2.parameters == options

    database.iaas.delete(db, id=iaas.id)
    assert database.iaas.get(db, id=iaas.id) is None


def test_parse_options(db: Session) -> None:
    options = [
        IaasOption(name="name", type='str', secret=False),
    ]
    iaas_in = CreateIaas(name="test2", type=IaasType.PAAS, parameters=options)
    iaas = Iaas.from_orm(database.iaas.create(db, obj_in=iaas_in))

    assert iaas.parameters == options
    database.iaas.delete(db, id=iaas.id)
