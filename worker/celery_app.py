from celery import Celery
import config

celery_app = Celery(
    "steno_worker",
    broker=config.REDIS_URL,
    backend=config.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,
)