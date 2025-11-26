# app/core/celery_app.py
from celery import Celery
from celery.schedules import crontab
from kombu import Queue

from app.core.config import settings

celery_app = Celery(
    "docuflow",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.documents"],
)

celery_app.conf.task_routes = {
    "app.tasks.documents.*": {"queue": "documents"},
}

celery_app.conf.timezone = "UTC"

celery_app.conf.beat_schedule = {
    "retry-failed-documents-every-5-min": {
        "task": "app.tasks.documents.retry_failed_documents",
        "schedule": crontab(minute="*/5"),  # cada 5 minutos
    },
}
