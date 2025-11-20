"""CSV parsing helpers."""

from __future__ import annotations

import csv
from typing import Dict, Iterable, List, Optional


def _parse_bool(value: Optional[str]) -> Optional[bool]:
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    return None


def chunk_products(file_path: str, chunk_size: int = 10000) -> Iterable[List[Dict]]:
    """
    Stream CSV rows in chunks.

    Expected columns: sku, name, description, price, active
    """
    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        buffer: List[Dict] = []
        for row in reader:
            sku = (row.get("sku") or "").strip()
            if not sku:
                # Skip invalid rows without SKU
                continue

            cleaned = {
                "sku": sku,
                "name": (row.get("name") or "").strip() or None,
                "description": (row.get("description") or "").strip() or None,
                "price": _parse_price(row.get("price")),
                "active": _parse_bool(row.get("active")),
            }
            buffer.append(cleaned)
            if len(buffer) >= chunk_size:
                yield buffer
                buffer = []

        if buffer:
            yield buffer


def _parse_price(value: Optional[str]) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None
