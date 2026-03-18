"""Esquemas Pydantic para el módulo Business (Productos, Precios, Inventario)."""
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field


class CountryBase(BaseModel):
    code: str = Field(..., max_length=2)
    name: str
    currency_code: str | None = Field(None, max_length=3)
    default_tax_rate: Decimal | None = None


class CountryCreate(CountryBase):
    pass


class CountryResponse(CountryBase):
    class Config:
        from_attributes = True


class ProductPriceBase(BaseModel):
    country_code: str = Field(..., max_length=2)
    net_price: Decimal = Field(..., ge=0)
    tax_rate: Decimal = Field(..., ge=0)
    is_exempt: bool = False


class ProductPriceCreate(ProductPriceBase):
    pass


class ProductPriceUpdate(BaseModel):
    net_price: Decimal | None = Field(None, ge=0)
    tax_rate: Decimal | None = Field(None, ge=0)
    is_exempt: bool | None = None


class ProductPriceResponse(ProductPriceBase):
    id: UUID
    product_id: UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class InventoryBase(BaseModel):
    quantity: int = Field(default=0, ge=0)


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    quantity: int = Field(..., ge=0)


class InventoryResponse(InventoryBase):
    id: UUID
    product_id: UUID
    last_updated: datetime | None = None

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    sku: str = Field(..., max_length=100)
    name: str
    description: str | None = None
    category: str | None = Field(None, max_length=100)


class ProductCreate(ProductBase):
    initial_quantity: int = Field(default=0, ge=0)


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = Field(None, max_length=100)


class ProductResponse(ProductBase):
    id: UUID
    created_at: datetime | None = None
    precios: list[ProductPriceResponse] = []
    inventory: InventoryResponse | None = None

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    id: UUID
    sku: str
    name: str
    category: str | None
    quantity: int = 0

    class Config:
        from_attributes = True
