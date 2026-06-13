# backend/app/core/celery_app.py
from celery import Celery

# Initialize Celery
# broker: Where tasks are sent (Redis)
# backend: Where the results of the tasks are stored (Redis)
celery_app = Celery(
    "mycelia_worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1"
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Prevent memory leaks by restarting workers after 100 tasks
    worker_max_tasks_per_child=100 
)