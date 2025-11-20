"""Celery application configuration and factory."""

from celery import Celery

from app.config import get_settings


def create_celery_app() -> Celery:
    """Create and configure Celery application."""
    settings = get_settings()
    celery = Celery(
        "product_importer",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
        include=["app.tasks.importer", "app.tasks.webhook_sender"],
    )
    celery.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        task_track_started=True,
    )
    return celery


celery_app = create_celery_app()

