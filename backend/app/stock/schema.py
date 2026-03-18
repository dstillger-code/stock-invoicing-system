"""Esquemas Pydantic para el módulo Stock."""
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class StockItemBase(BaseModel):
    sku: str = Field(..., min_length=1, max_length=64)
    nombre: str = Field(..., min_length=1, max_length=255)
    cantidad: int = Field(default=0, ge=0)
    precio_base: Decimal = Field(default=Decimal("0"), ge=0)


class StockItemCreate(StockItemBase):
    pass


class StockItemUpdate(BaseModel):
    nombre: str | None = Field(None, min_length=1, max_length=255)
    cantidad: int | None = Field(None, ge=0)
    precio_base: Decimal | None = Field(None, ge=0)


class StockItemResponse(StockItemBase):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
