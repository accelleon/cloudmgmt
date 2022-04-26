from datetime import datetime


def current_period() -> str:
    now = datetime.utcnow()
    return now.strftime("%Y-%m")


def date_to_period(date: datetime) -> str:
    return date.strftime("%Y-%m")
