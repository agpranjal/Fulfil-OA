"""Webhook service layer."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Webhook
from app.schemas import WebhookCreate, WebhookRead, WebhookUpdate


class WebhookService:
    """Encapsulate webhook operations."""

    def __init__(self, db: Session):
        self.db = db

    def list_webhooks(self) -> List[WebhookRead]:
        webhooks = self.db.execute(select(Webhook).order_by(Webhook.id.desc())).scalars().all()
        return [WebhookRead.model_validate(w) for w in webhooks]

    def create_webhook(self, payload: WebhookCreate) -> WebhookRead:
        webhook = Webhook(url=str(payload.url), event_type=payload.event_type, active=payload.active)
        self.db.add(webhook)
        self.db.commit()
        self.db.refresh(webhook)
        return WebhookRead.model_validate(webhook)

    def update_webhook(self, webhook_id: int, payload: WebhookUpdate) -> Optional[WebhookRead]:
        webhook = self.db.get(Webhook, webhook_id)
        if not webhook:
            return None
        if payload.url is not None:
            webhook.url = str(payload.url)
        if payload.event_type is not None:
            webhook.event_type = payload.event_type
        if payload.active is not None:
            webhook.active = payload.active
        self.db.commit()
        self.db.refresh(webhook)
        return WebhookRead.model_validate(webhook)

    def delete_webhook(self, webhook_id: int) -> bool:
        webhook = self.db.get(Webhook, webhook_id)
        if not webhook:
            return False
        self.db.delete(webhook)
        self.db.commit()
        return True
