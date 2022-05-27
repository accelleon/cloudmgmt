from typing import Tuple
import pytz
from datetime import datetime

from asgiref.sync import sync_to_async
from dateutil.relativedelta import relativedelta


def range_from_month(month: str) -> Tuple[datetime, datetime]:
    """
    Returns the first and last day of the given month with UTC 00:00:00.000.
    """
    date = datetime.strptime(month, "%Y-%m")
    return (
        date.replace(day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=pytz.UTC),
        date.replace(tzinfo=pytz.UTC)
        + relativedelta(months=1, day=1, hour=0, minute=0, second=0, microsecond=0),
    )


def current_month_date_range() -> Tuple[datetime, datetime]:
    """
    Returns the first and last day of the current month with UTC 00:00:00.000.
    """
    return (
        datetime.now().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=pytz.UTC
        ),
        datetime.now().replace(tzinfo=pytz.UTC)
        + relativedelta(months=1, day=1, hour=0, minute=0, second=0, microsecond=0),
    )


# Pydantic hates sync_to_async as a decorator
def as_async(func):
    def wrapper(*args, **kwargs):
        return sync_to_async(func)(*args, **kwargs)

    return wrapper
