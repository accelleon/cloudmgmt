from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from pycloud.utils import current_month_date_range
from app import database
from app.model.account import CreateAccount
from app.model.billing import CreateBillingPeriod, UpdateBillingPeriod, BillingPeriod

from app.tests.utils import random_username


def test_create(
    db: Session,
) -> None:
    iaas = database.iaas.get_by_name(db, name="Jelastic")
    assert iaas
    data = CreateAccount(
        name=random_username(),
        iaas="Jelastic",
        data={"endpoint": "Layershift", "api_key": "test"},
    )
    acct = database.account.create(db, obj_in=data)
    assert acct

    (start, end) = current_month_date_range()

    obj_in = CreateBillingPeriod(
        account_id=acct.id,
        total=100,
        balance=50,
        start_date=start,
        end_date=end,
    )
    bill = database.billing.create(db, obj_in=obj_in)
    assert bill
    assert bill.account.id == acct.id
    assert bill.account.iaas_id == iaas.id
    assert bill.total == 100
    assert bill.balance == 50
    assert bill.start_date == start
    assert bill.end_date == end
