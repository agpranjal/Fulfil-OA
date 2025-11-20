"""Administrative routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["admin"])


@router.delete("", status_code=status.HTTP_200_OK)
def delete_all_products(confirm: bool = Query(False), db: Session = Depends(get_db)):
    """Delete all products. Requires confirm=true to proceed."""
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Confirmation required. Pass confirm=true to delete all products.",
        )
    service = ProductService(db)
    deleted = service.delete_all_products()
    return {"deleted": deleted}
