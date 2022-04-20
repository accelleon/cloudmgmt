from pytz import utc

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.event import listens_for
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

from app.database.session import SessionLocal
from app import database
from .billing import get_billing

scheduler: AsyncIOScheduler = None


async def setup_scheduler() -> None:
    """
    Setup the scheduler and tasks.
    """
    jobstores = {
        # No need to use a persistent job store
        # Just create the jobs on start
        "default": MemoryJobStore(),
    }
    executors = {
        "default": ThreadPoolExecutor(max_workers=10),
    }
    job_defaults = {
        "coalesce": False,
        "max_instances": 1,
    }
    global scheduler
    scheduler = AsyncIOScheduler(
        jobstores=jobstores,
        executors=executors,
        job_defaults=job_defaults,
        timezone=utc,
    )
    scheduler.start()

    # Add billing task for all accounts
    db: AsyncSession = SessionLocal()
    accounts = await database.account.get_multi(db)
    for account in accounts:
        scheduler.add_job(
            func=get_billing,
            trigger=CronTrigger(
                minute="0",
                hour="0",
                day_of_week="*",
                day="*",
                month="*",
            ),
            args=[account.id],
            id=f"billing-{account.id}",
        )


@listens_for(database.Account, "after_insert")
def account_inserted(mapper, connection, target: database.Account) -> None:
    """
    Add billing task for the new account.
    """
    scheduler.add_job(
            func=get_billing,
            trigger=CronTrigger(
                minute="0",
                hour="0",
                day_of_week="*",
                day="*",
                month="*",
            ),
            args=[target.id],
            id=f"billing-{target.id}",
        )


@listens_for(database.Account, "before_delete")
def account_deleted(mapper, connection, target: database.Account) -> None:
    """
    Remove billing task for the deleted account.
    """
    scheduler.remove_job(f"billing-{target.id}")
