from sqlalchemy.exc import IntegrityError
from celery import shared_task, group

from dateutil.relativedelta import relativedelta

from .utils import run_sync
from app.database.session import SessionLocal
from app import database, model

from pycloud import CloudFactory
from pycloud.exc import UnknownError, RateLimit, AuthorizationError


@shared_task(name="get_billing", bind=True)
@run_sync
async def get_billing(self, account_id: int) -> None:
    """
    Creates or updates billing period for the current month for the given account.
    """
    async with SessionLocal() as db:
        account = await database.account.get(db, id=account_id)

        if account is None:
            raise Exception("Account not found")

        client = CloudFactory.get_client(
            account.iaas.name,
            account.data,  # type: ignore
        )

        try:
            billing = await client.get_current_invoiced()
        except AuthorizationError as e:
            account.last_error = str(e)
            account.validated = False
            db.add(account)
            db.commit()
            raise
        except (UnknownError, RateLimit) as e:
            raise self.retry(exc=e, countdown=60)

        period = (billing.end_date - relativedelta(days=1)).strftime("%Y-%m")

        new_obj = model.CreateBillingPeriod(
            **billing.dict(),
            account_id=account_id,
        )
        try:
            await database.billing.create(db, obj_in=new_obj)
        except IntegrityError:
            await db.rollback()
            db_obj = await database.billing.get_account_period(
                db,
                account_id=account_id,
                period=period,
            )
            obj_in = model.UpdateBillingPeriod(
                **billing.dict(),
            )
            await database.billing.update(db, db_obj=db_obj, obj_in=obj_in)  # type: ignore

        if not account.validated:
            account.validated = True
        if account.last_error:
            account.last_error = None
        db.add(account)
        await db.commit()


@shared_task(name="get_billing_all")
@run_sync
async def get_all_billing() -> None:
    """
    Creates or updates billing period for the current month for all accounts.
    """
    async with SessionLocal() as db:
        accounts = await database.account.get_all(db)

        group(get_billing.s(account.id) for account in accounts)()
