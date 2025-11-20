"""Webhook sender Celery task."""

import json
import time
from typing import Dict

import httpx

from app.celery_app import celery_app
from app.config import get_settings


@celery_app.task(name="app.tasks.send_webhook")
def send_webhook_task(webhook_id: int, url: str, payload: Dict) -> Dict:
    """Send webhook payload and capture response metadata."""
    settings = get_settings()
    start = time.perf_counter()
    try:
        resp = httpx.post(url, json=payload, timeout=settings.webhook_timeout_seconds)
        elapsed = (time.perf_counter() - start) * 1000  # ms
        return {"webhook_id": webhook_id, "status_code": resp.status_code, "elapsed_ms": round(elapsed, 2), "error": None}
    except Exception as exc:  # noqa: BLE001
        elapsed = (time.perf_counter() - start) * 1000  # ms
        return {"webhook_id": webhook_id, "status_code": None, "elapsed_ms": round(elapsed, 2), "error": str(exc)}
