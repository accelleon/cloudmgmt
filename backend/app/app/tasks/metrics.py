from datetime import datetime, tzinfo
from pytz import UTC

from sqlalchemy.exc import IntegrityError
from celery import shared_task, group

from pycloud.base import CloudBase
from pycloud.models import IaasType

from .utils import run_sync
from app.database.session import SessionLocal
from app import database, model

from pycloud import CloudFactory
from pycloud.exc import UnknownError, RateLimit, AuthorizationError


@shared_task(name="get_instance_count", bind=True)
@run_sync
async def get_instance_count(self, account_id: int) -> None:
    time = datetime.utcnow()
    async with SessionLocal() as db:
        account = await database.account.get(db, id=account_id)
        if account is None:
            raise Exception("Account not found")
        if account.iaas.type == model.IaasType.SIP:
            raise Exception("Account is SIP account")

        client: CloudBase = CloudFactory.get_client(
            account.iaas.name,
            account.data,  # type: ignore
        )

        try:
            server_count = await client.get_instance_count()
        except AuthorizationError as e:
            account.last_error = str(e)
            account.validated = False
            db.add(account)
            db.commit()
            raise
        except (UnknownError, RateLimit) as e:
            print(f"{account.name} {account.iaas.name} {e}")
            raise self.retry(exc=e, countdown=60)

        await database.metric.create(
            db, account_id=account_id, time=time, instances=server_count
        )


@shared_task(name="get_instance_count_all", bind=True)
@run_sync
async def get_instance_count_all(self) -> None:
    async with SessionLocal() as db:
        accounts = await database.account.get_all(db)
        if not accounts:
            raise Exception("No accounts found")

        group(
            get_instance_count.s(account.id)
            for account in accounts
            if account.iaas.type != IaasType.SIP
        )()
