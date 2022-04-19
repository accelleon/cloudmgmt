import pytest
from sqlalchemy.ext.asyncio import AsyncSession as Session
from sqlalchemy.exc import IntegrityError

from app import database
from app.model.account import AccountFilter, CreateAccount, UpdateAccount
from app.tests.utils import random_username


@pytest.mark.asyncio
async def test_create_delete(
    db: Session,
) -> None:
    iaas = await database.iaas.get_by_name(db, name="Jelastic")
    assert iaas
    data = CreateAccount(
        name=random_username(),
        iaas="Jelastic",
        data={"endpoint": "Layershift", "api_key": "test"},
    )
    acct = await database.account.create(db, obj_in=data)
    assert acct.name == data.name
    assert acct.iaas_id == iaas.id
    assert acct.data == data.data
    assert acct.currency == "GBP"

    assert acct.iaas.name == iaas.name  # Check our relationships

    await database.account.delete(db, id=acct.id)
    assert await database.account.get(db, id=acct.id) is None


@pytest.mark.asyncio
async def test_create_missing_param(
    db: Session,
) -> None:
    data = CreateAccount(
        name=random_username(),
        iaas="Jelastic",
        data={"endpoint": "Layershift"},
    )
    with pytest.raises(ValueError):
        await database.account.create(db, obj_in=data)


@pytest.mark.asyncio
async def test_create_wrong_iaas(
    db: Session,
) -> None:
    data = CreateAccount(
        name="test",
        iaas="Potato",
        data={"endpoint": "Layershift", "api_key": "test"},
    )
    with pytest.raises(ValueError):
        await database.account.create(db, obj_in=data)


@pytest.mark.asyncio
async def test_create_duplicate(
    db: Session,
) -> None:
    iaas = await database.iaas.get_by_name(db, name="Jelastic")
    assert iaas
    data = CreateAccount(
        name=random_username(),
        iaas="Jelastic",
        data={"endpoint": "Layershift", "api_key": "test"},
    )
    _ = await database.account.create(db, obj_in=data)
    with pytest.raises(IntegrityError):
        await database.account.create(db, obj_in=data)
    await db.rollback()


@pytest.mark.asyncio
async def test_filter_iaas(
    db: Session,
) -> None:
    iaas = await database.iaas.get_by_name(db, name="Jelastic")
    assert iaas
    data = CreateAccount(
        name=random_username(),
        iaas="Jelastic",
        data={"endpoint": "Layershift", "api_key": "test"},
    )
    _ = await database.account.create(db, obj_in=data)

    accts, total = await database.account.filter(
        db, filter=AccountFilter(iaas="Jelastic")
    )
    assert total
    for a in accts:
        assert a.iaas.name == "Jelastic"


@pytest.mark.asyncio
async def test_filter_name(
    db: Session,
) -> None:
    iaas = await database.iaas.get_by_name(db, name="Jelastic")
    assert iaas
    data = CreateAccount(
        name=random_username(),
        iaas="Jelastic",
        data={"endpoint": "Layershift", "api_key": "test"},
    )
    _ = await database.account.create(db, obj_in=data)

    accts, total = await database.account.filter(
        db, filter=AccountFilter(iaas="Jelastic", name=data.name)
    )
    print(accts)
    assert total == 1
    assert accts[0].name == data.name


@pytest.mark.asyncio
async def test_update(
    db: Session,
) -> None:
    data = CreateAccount(
        name=random_username(),
        iaas="Jelastic",
        data={"endpoint": "Layershift", "api_key": "test"},
    )
    acct = await database.account.create(db, obj_in=data)

    data2 = UpdateAccount(
        name=random_username(),
        data={"endpoint": "Layershift", "api_key": "test2"},
    )
    acct = await database.account.update(db, db_obj=acct, obj_in=data2)
    assert acct.name != data.name
    assert acct.name == data2.name
    assert acct.data == data2.data


@pytest.mark.asyncio
async def test_update_duplicate(
    db: Session,
) -> None:
    data = CreateAccount(
        name=random_username(),
        iaas="Jelastic",
        data={"endpoint": "Layershift", "api_key": "test"},
    )
    acct = await database.account.create(db, obj_in=data)
    data = CreateAccount(
        name=random_username(),
        iaas="Jelastic",
        data={"endpoint": "Layershift", "api_key": "test2"},
    )
    await database.account.create(db, obj_in=data)
    data2 = UpdateAccount(
        name=data.name,
        data={"endpoint": "Layershift", "api_key": "test2"},
    )
    with pytest.raises(IntegrityError):
        await database.account.update(db, db_obj=acct, obj_in=data2)
    await db.rollback()
