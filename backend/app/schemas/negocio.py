"""Esquemas Pydantic para el módulo Negocio (Productos y Precios)."""
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class PrecioPorRegionBase(BaseModel):
    region: str = Field(..., min_length=1, max_length=10)
    precio_neto: Decimal = Field(..., ge=0)
    tipo_iva: Decimal = Field(default=Decimal("0"), ge=0)
    observaciones: str | None = None


class PrecioPorRegionCreate(PrecioPorRegionBase):
    pass


class PrecioPorRegionUpdate(BaseModel):
    precio_neto: Decimal | None = Field(None, ge=0)
    tipo_iva: Decimal | None = Field(None, ge=0)
    observaciones: str | None = None


class PrecioPorRegionResponse(PrecioPorRegionBase):
    id: int
    producto_id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class ProductoBase(BaseModel):
    sku: str = Field(..., min_length=1, max_length=50)
    nombre: str = Field(..., min_length=1, max_length=255)
    descripcion: str | None = None
    categoria: str | None = Field(None, max_length=100)


class ProductoCreate(ProductoBase):
    precios: list[PrecioPorRegionCreate] = []


class ProductoUpdate(BaseModel):
    nombre: str | None = Field(None, min_length=1, max_length=255)
    descripcion: str | None = None
    categoria: str | None = Field(None, max_length=100)


class ProductoResponse(ProductoBase):
    id: int
    is_active: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
    precios: list[PrecioPorRegionResponse] = []

    class Config:
        from_attributes = True


class ProductoListResponse(BaseModel):
    id: int
    sku: str
    nombre: str
    categoria: str | None
    is_active: int

    class Config:
        from_attributes = True
