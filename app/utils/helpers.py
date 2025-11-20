"""Shared helper utilities."""

from math import ceil
from typing import List, Optional, Tuple


def normalize_sku(sku: str) -> str:
    """Normalize SKU casing."""
    return sku.lower()


def paginate(total_count: int, page: int, limit: int) -> Tuple[int, int, int]:
    """Return (page, total_pages, offset)."""
    total_pages = ceil(total_count / limit) if limit else 1
    offset = (page - 1) * limit
    return page, total_pages, offset


def apply_pagination(query, page: int, limit: int):
    """Apply pagination to a SQLAlchemy query."""
    if limit:
        query = query.limit(limit)
    if page and limit:
        query = query.offset((page - 1) * limit)
    return query
