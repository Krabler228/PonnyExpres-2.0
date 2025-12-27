from celery import Celery
from celery.schedules import crontab

from src.app.core.config import settings


celery_app = Celery(
    "parcel_service",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["src.app.tasks.parcels", "src.app.tasks.recalculate_delivery"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,
    worker_prefetch_multiplier=1,
)

celery_app.conf.beat_schedule = {
    "recalculate-delivery-cost-every-5-min": {
        "task": "src.app.tasks.recalculate_delivery.recalculate_delivery_costs",
        "schedule": crontab(minute="*/5"),
    }
}


def get_celery_app():
    return celery_app
