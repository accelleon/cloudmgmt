from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import SessionLocal
from app import database, model
from pycloud import CloudFactory


async def get_billing(account_id: int) -> None:
    """
    Creates or updates billing period for the current month for the given account.
    """
    db: AsyncSession = SessionLocal()

    account = await database.account.get(db, id=account_id)

    if account is None:
        raise Exception("Account not found")

    client = CloudFactory.get_client(
        account.iaas.name,
        account.data,  # type: ignore
    )

    billing = await client.get_current_billing()

    new_obj = model.CreateBillingPeriod(
        **billing.dict(),
        account_id=account_id,
    )
    try:
        await database.billing.create(db, obj_in=new_obj)
    except IntegrityError:
        await db.rollback()
        db_obj = await database.billing.get_by_period(
            db,
            account_id=account_id,
            start_date=billing.start_date,
            end_date=billing.end_date,
        )
        obj_in = model.UpdateBillingPeriod(
            **billing.dict(),
        )
        await database.billing.update(db, db_obj=db_obj, obj_in=obj_in)  # type: ignore
