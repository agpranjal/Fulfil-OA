"""Pydantic schemas."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, HttpUrl, field_validator


class ProductBase(BaseModel):
    sku: str
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    active: Optional[bool] = True

    @field_validator("sku")
    @classmethod
    def normalize_sku(cls, value: str) -> str:
        """Normalize SKU casing and spacing."""
        return value.strip().lower()


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    active: Optional[bool] = None


class ProductRead(ProductBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class WebhookBase(BaseModel):
    url: HttpUrl
    event_type: str
    active: Optional[bool] = True


class WebhookCreate(WebhookBase):
    pass


class WebhookUpdate(BaseModel):
    url: Optional[HttpUrl] = None
    event_type: Optional[str] = None
    active: Optional[bool] = None


class WebhookRead(WebhookBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UploadStatus(BaseModel):
    status: str
    processed: int
    total: int
    percent: float
    message: Optional[str] = None
