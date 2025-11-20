"""CSV importer Celery task placeholder."""

from app.celery_app import celery_app


@celery_app.task(name="app.tasks.import_products")
def import_products_task(*_args, **_kwargs):
    """Process CSV import; implementation to be added in later tasks."""
    return {"status": "not_implemented"}

