from celery import Celery
from celery.schedules import crontab

from app import tasks  # noqa

app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["app.tasks"],
)


app.conf.beat_schedule = {
    "get_billing_all": {
        "task": "get_billing_all",
        "schedule": crontab(hour=0, minute=0),
    },
}
