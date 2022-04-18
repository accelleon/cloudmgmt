import pytest
from sqlalchemy.orm import Session

from app import database, model
from app.tasks import get_billing
from app.tests.utils import random_username


@pytest.mark.usefixtures("celery_session_app")
@pytest.mark.usefixtures("celery_session_worker")
class Test_Billing:
    def test_billing(
        self,
        db: Session,
    ) -> None:
        data = model.CreateAccount(
            name=random_username(),
            iaas="Jelastic",
            data={
                "endpoint": "Layershift",
                "api_key": "asdf",
            },
        )
        acct = database.account.create(db, obj_in=data)

        get_billing.delay(acct.id).get()

        acct2 = database.account.get(db, id=acct.id)
        assert acct2
        assert acct2.bills
