"""CSV importer Celery task."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import Product
from app.utils.csv_parser import chunk_products


def _upsert_products(session, products_chunk) -> int:
    """Upsert a chunk of products and return count processed."""
    for product_data in products_chunk:
        sku = product_data["sku"].lower()
        existing = session.execute(select(Product).where(Product.sku == sku)).scalars().first()
        if existing:
            existing.name = product_data.get("name", existing.name)
            existing.description = product_data.get("description", existing.description)
            if product_data.get("price") is not None:
                existing.price = product_data["price"]
            if product_data.get("active") is not None:
                existing.active = product_data["active"]
        else:
            session.add(Product(**product_data))
    session.commit()
    return len(products_chunk)


@celery_app.task(bind=True, name="app.tasks.import_products")
def import_products_task(self, file_path: str, total_rows: Optional[int] = None, chunk_size: int = 10000):
    """
    Process CSV import in chunks.

    Args:
        file_path: Path to uploaded CSV file.
        total_rows: Optional total count for percent calculations.
        chunk_size: Batch size for DB writes.
    """
    processed = 0
    total = total_rows or 0
    self.update_state(
        state="PROGRESS",
        meta={"status": "processing", "processed": processed, "total": total, "percent": 0.0, "message": "Starting"},
    )

    try:
        for chunk in chunk_products(file_path, chunk_size=chunk_size):
            with SessionLocal() as session:
                processed += _upsert_products(session, chunk)
            current_total = total or processed
            percent = round((processed / current_total) * 100, 2) if current_total else 0.0
            self.update_state(
                state="PROGRESS",
                meta={
                    "status": "processing",
                    "processed": processed,
                    "total": current_total,
                    "percent": percent,
                    "message": f"Processed {processed} rows",
                },
            )

        final_total = total or processed
        return {
            "status": "completed",
            "processed": processed,
            "total": final_total,
            "percent": 100.0 if final_total else 0.0,
            "message": "Completed",
        }

    except (SQLAlchemyError, OSError, ValueError) as exc:
        current_total = total or processed or 1
        percent = round((processed / current_total) * 100, 2)
        self.update_state(
            state="FAILURE",
            meta={
                "status": "error",
                "processed": processed,
                "total": current_total,
                "percent": percent,
                "message": str(exc),
            },
        )
        raise
