import pytest
from sqlalchemy.ext.asyncio import AsyncSession as Session

from app.database import template, account
from app.model import CreateTemplate, UpdateTemplate, TemplateFilter, CreateAccount
from app.tests.utils import random_username


@pytest.mark.asyncio
async def test_template_exists(
    db: Session,
) -> None:
    templateDb = await template.get_by_name(db, name="default")
    assert templateDb is not None
    assert templateDb.name == "default"


@pytest.mark.asyncio
async def test_template_create(
    db: Session,
) -> None:
    accounts = await account.get_all(db)
    account_ids = [account.id for account in accounts]
    template_obj = CreateTemplate(
        name=random_username(),
        description="test",
        order=account_ids,
    )
    templateDb = await template.create(db, obj_in=template_obj)
    assert templateDb.orders
    assert len(templateDb.orders) == len(account_ids)
    template_ids = [order.account_id for order in templateDb.orders]
    for id in account_ids:
        assert id in template_ids


@pytest.mark.asyncio
async def test_template_update(
    db: Session,
) -> None:
    accounts = await account.get_all(db)
    account_ids = [account.id for account in accounts]
    template_obj = CreateTemplate(
        name=random_username(),
        description="test",
        order=account_ids,
    )
    templateDb = await template.create(db, obj_in=template_obj)
    account_ids2 = list(reversed(account_ids))
    update_obj = UpdateTemplate(
        order=account_ids2,
    )
    new_obj = await template.update(db, db_obj=templateDb, obj_in=update_obj)
    orders = [order.account_id for order in new_obj.orders]
    assert orders != account_ids
    assert orders == account_ids2


@pytest.mark.asyncio
async def test_auto_add(
    db: Session,
) -> None:
    accounts = await account.get_all(db)
    account_ids = [account.id for account in accounts]
    template_obj = CreateTemplate(
        name=random_username(),
        description="test",
        order=account_ids,
    )
    templateDb = await template.create(db, obj_in=template_obj)

    # Create a new account
    data = CreateAccount(
        name=random_username(),
        iaas="Jelastic",
        data={"endpoint": "Layershift", "api_key": "test"},
    )
    acct = await account.create(db, obj_in=data)

    # get the template
    template2 = await template.get(db, id=templateDb.id)
    assert template2
    assert acct.id not in [order.account_id for order in template2.orders]
