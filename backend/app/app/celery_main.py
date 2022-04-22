from celery import Celery
from celery.schedules import crontab

from app.tasks import get_all_billing, get_billing

app = Celery("tasks", broker="redis://localhost:6379/0")


app.conf.beat_schedule = {
    "get_all_billing": {
        "task": "app.tasks.get_all_billing",
        "schedule": crontab(hour=0, minute=0),
    },
}
