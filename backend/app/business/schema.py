"""Esquemas Pydantic para configuración de empresa."""
from datetime import datetime
from pydantic import BaseModel, EmailStr


class CompanySettingsResponse(BaseModel):
    country_code: str
    company_name: str
    logo_url: str | None
    tax_id: str | None
    address: str | None
    phone: str | None
    email: str | None
    updated_at: datetime | None

    class Config:
        from_attributes = True


class CompanySettingsUpdate(BaseModel):
    company_name: str | None = None
    tax_id: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
