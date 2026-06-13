# backend/app/core/celery_app.py
from celery import Celery

# Initialize Celery
celery_app = Celery(
    "mycelia_worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
    # ---> ADD THIS LINE BELOW <---
    include=["app.features.jobs.worker"] 
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_max_tasks_per_child=100 
)