import asyncio
from random import choice, random
from datetime import datetime
from math import floor

from dateutil.relativedelta import relativedelta

from app.database.session import SessionLocal
from app import database, model
from app.tests.utils import random_username
from pycloud.utils import current_month_date_range, range_from_month


async def main() -> None:
    async with SessionLocal() as db:
        providers = await database.iaas.get_all(db)
        for _ in range(10):
            # create 10 random accounts
            iaas = choice(providers)
            data = {}
            for param in iaas.params:
                if param["type"] == "choice":
                    data[param["key"]] = choice(param["choices"])
                else:
                    data[param["key"]] = "test"

            obj = model.CreateAccount(
                name=random_username(),
                iaas=iaas.name,
                data=data,
            )
            acct = await database.account.create(db, obj_in=obj)

            # create a billing period
            start, end = current_month_date_range()
            bill = model.CreateBillingPeriod(
                account_id=acct.id,
                total=random() * 100.0,
                balance=random() * 100.0,
                start_date=start,
                end_date=end,
            )

            await database.billing.create(db, obj_in=bill)

            # Fill in BS metrics
            for i in range(50):
                await database.metric.create(
                    db,
                    account_id=acct.id,
                    time=start + relativedelta(minutes=(i * 5)),
                    instances=floor(random() * 100),
                )

            # and create one for last month
            start, end = range_from_month(
                (datetime.today() - relativedelta(months=1)).strftime("%Y-%m")
            )
            bill = model.CreateBillingPeriod(
                account_id=acct.id,
                total=random() * 100.0,
                balance=random() * 100.0,
                start_date=start,
                end_date=end,
            )

            await database.billing.create(db, obj_in=bill)


if __name__ == "__main__":
    asyncio.run(main())
