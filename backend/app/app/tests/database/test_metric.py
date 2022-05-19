from random import choice
from datetime import datetime

import pytest
from dateutil.relativedelta import relativedelta
from sqlalchemy.ext.asyncio import AsyncSession as Session
from sqlalchemy.exc import IntegrityError

from app import database
from pycloud.utils import current_month_date_range, range_from_month


@pytest.mark.asyncio
async def test_resample(
    db: Session,
) -> None:
    # Find a random account
    acct = choice(await database.account.get_all(db))
    assert acct
    start, end = range_from_month(
        (datetime.today() - relativedelta(months=1)).strftime("%Y-%m")
    )
    metrics = await database.metric.filter(
        db, account=acct, start=start, end=end, period="5min"
    )
