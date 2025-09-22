from celery import Celery

celery_app = Celery(
    "ems6",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/1"
)

celery_app.conf.task_routes = {
    "app.tasks.email_tasks.*": {"queue": "email_queue"},
}
