import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library_project.settings")

app = Celery(
    "library_project",
    broker="redis://localhost",
    backend="redis://localhost"
)

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
