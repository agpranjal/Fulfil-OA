"""Webhook sender Celery task placeholder."""

from app.celery_app import celery_app


@celery_app.task(name="app.tasks.send_webhook")
def send_webhook_task(*_args, **_kwargs):
    """Send webhook; implementation to be added in later tasks."""
    return {"status": "not_implemented"}

