from celery import Celery

app = Celery("tasks", broker="redis://", backend="redis://")
app.autodiscover_tasks(["tasks"])
