import os
from celery import Celery

celery_app = Celery(
    "asm_platform",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1"),
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    worker_prefetch_multiplier=1,
    worker_concurrency=int(os.getenv("SCAN_CONCURRENCY", "3")),
    task_acks_late=True,
    task_time_limit=1200,
)
