from typing import Tuple
import pytz
from datetime import datetime

from dateutil.relativedelta import relativedelta


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
