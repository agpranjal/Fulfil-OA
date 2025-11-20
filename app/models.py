"""SQLAlchemy models."""

from sqlalchemy import Boolean, Column, Integer, String, Text, Numeric, event
from sqlalchemy.sql import expression

from app.database import Base


class Product(Base):
    """Product entity."""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=True)
    active = Column(Boolean, server_default=expression.true(), nullable=False)


class Webhook(Base):
    """Webhook endpoint entity."""

    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(Text, nullable=False)
    event_type = Column(String, nullable=False)
    active = Column(Boolean, server_default=expression.true(), nullable=False)


@event.listens_for(Product, "before_insert")
@event.listens_for(Product, "before_update")
def normalize_product_sku(mapper, connection, target) -> None:  # type: ignore[override]
    """Force SKU to lowercase for case-insensitive uniqueness."""
    if target.sku:
        target.sku = target.sku.lower()
