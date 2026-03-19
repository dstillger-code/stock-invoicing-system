"""Esquemas Pydantic para el módulo Products."""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class ProductPriceResponse(BaseModel):
    id: str
    net_price: float

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    sku: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    category: str | None = Field(None, max_length=100)


class ProductCreate(ProductBase):
    net_price: float | None = Field(None, ge=0)
    initial_quantity: int | None = Field(0, ge=0)


class ProductUpdate(BaseModel):
    sku: str | None = Field(None, min_length=1, max_length=100)
    name: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    category: str | None = Field(None, max_length=100)
    is_active: bool | None = None
    net_price: float | None = Field(None, ge=0)


class ProductResponse(ProductBase):
    id: UUID
    is_active: bool
    country_code: str
    created_at: datetime | None = None
    quantity: int = 0
    prices: list[ProductPriceResponse] = []

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    id: UUID
    sku: str
    name: str
    description: str | None
    category: str | None
    is_active: bool
    country_code: str
    created_at: datetime | None = None
    quantity: int = 0
    prices: list[ProductPriceResponse] = []

    class Config:
        from_attributes = True
