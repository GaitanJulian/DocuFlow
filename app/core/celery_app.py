from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "docuflow",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Buscamos tareas dentro del paquete app.tasks
celery_app.autodiscover_tasks(["app.tasks"])
