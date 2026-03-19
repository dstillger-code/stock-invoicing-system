"""Esquemas Pydantic para el módulo Products."""
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field


class ProductPriceBase(BaseModel):
    country_code: str = Field(..., min_length=2, max_length=2)
    net_price: float = Field(..., ge=0)
    tax_rate: float = Field(..., ge=0, le=100)
    is_exempt: bool = False


class ProductPriceCreate(ProductPriceBase):
    pass


class ProductPriceResponse(ProductPriceBase):
    id: UUID

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    sku: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    category: str | None = Field(None, max_length=100)


class ProductCreate(ProductBase):
    prices: list[ProductPriceCreate] = Field(default_factory=list)


class ProductUpdate(BaseModel):
    sku: str | None = Field(None, min_length=1, max_length=100)
    name: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    category: str | None = Field(None, max_length=100)
    is_active: bool | None = None


class ProductPriceUpdate(BaseModel):
    country_code: str
    net_price: Decimal | None = Field(None, ge=0)
    tax_rate: Decimal | None = Field(None, ge=0, le=100)
    is_exempt: bool | None = None


class ProductResponse(ProductBase):
    id: UUID
    is_active: bool
    created_at: datetime | None = None
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
    created_at: datetime | None = None
    quantity: int = 0
    prices: list[ProductPriceResponse] = []

    class Config:
        from_attributes = True
