"""Webhook routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import WebhookCreate, WebhookRead, WebhookUpdate
from app.services.webhook_service import WebhookService
from app.tasks.webhook_sender import send_webhook_task

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.get("", response_model=list[WebhookRead])
def list_webhooks(db: Session = Depends(get_db)) -> list[WebhookRead]:
    """List all webhooks."""
    service = WebhookService(db)
    return service.list_webhooks()


@router.post("", response_model=WebhookRead, status_code=status.HTTP_201_CREATED)
def create_webhook(payload: WebhookCreate, db: Session = Depends(get_db)) -> WebhookRead:
    """Create a webhook."""
    service = WebhookService(db)
    return service.create_webhook(payload)


@router.put("/{webhook_id}", response_model=WebhookRead)
def update_webhook(webhook_id: int, payload: WebhookUpdate, db: Session = Depends(get_db)) -> WebhookRead:
    """Update a webhook."""
    service = WebhookService(db)
    updated = service.update_webhook(webhook_id, payload)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found.")
    return updated


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_webhook(webhook_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a webhook."""
    service = WebhookService(db)
    deleted = service.delete_webhook(webhook_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found.")
    return None


@router.post("/test/{webhook_id}", status_code=status.HTTP_200_OK)
def test_webhook(webhook_id: int, db: Session = Depends(get_db)) -> dict:
    """Trigger webhook test task."""
    service = WebhookService(db)
    target = service.get_webhook(webhook_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found.")

    payload = {
        "event": "webhook.test",
        "timestamp": "2025-11-19T14:05:12Z",
        "message": "This is a test webhook fired from your product importer app.",
    }
    task = send_webhook_task.delay(webhook_id, str(target.url), payload)
    return {"task_id": task.id}
