"""Esquemas Pydantic para el módulo Facturación / Impuestos."""
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class TaxConfigBase(BaseModel):
    country_code: str = Field(..., min_length=2, max_length=2)
    country_name: str = Field(..., max_length=100)
    default_vat_rate: Decimal = Field(..., ge=0, le=100)
    extra_rates_json: str | None = None
    perception_enabled: bool = False
    perception_rates_json: str | None = None
    is_active: bool = True


class TaxConfigCreate(TaxConfigBase):
    pass


class TaxConfigResponse(TaxConfigBase):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
