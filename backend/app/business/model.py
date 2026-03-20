"""Modelos de configuración de la empresa."""
from sqlalchemy import Column, String, Text, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.base import Base


class CompanySettings(Base):
    """Configuración de empresa por país."""

    __tablename__ = "company_settings"
    __table_args__ = (
        UniqueConstraint("country_code", name="uq_company_settings_country"),
        {"schema": "business"},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=UUID("00000000-0000-0000-0000-000000000000"))
    country_code = Column(String(2), nullable=False)
    company_name = Column(Text, nullable=False, default="Mi Empresa")
    logo_url = Column(Text, nullable=True)
    tax_id = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    phone = Column(String(30), nullable=True)
    email = Column(String(255), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
