"""Modelos del esquema invoicing (facturación e impuestos)."""
from sqlalchemy import Column, String, Numeric, Boolean, Integer, DateTime, Text
from sqlalchemy.sql import func

from app.core.base import Base


class TaxConfig(Base):
    """
    Configuración de impuestos por país (motor internacional).
    Soporta Chile (IVA único 19%) y estructura para Argentina
    (múltiples alícuotas, percepciones) vía Strategy Pattern.
    """

    __tablename__ = "tax_config"
    __table_args__ = {"schema": "invoicing"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    country_code = Column(String(2), unique=True, index=True, nullable=False)  # CL, AR, ...
    country_name = Column(String(100), nullable=False)
    # IVA principal (ej. Chile 19%)
    default_vat_rate = Column(Numeric(5, 2), nullable=False)  # 19.00
    # Para Argentina: alícuotas adicionales en JSON o tabla relacionada
    extra_rates_json = Column(Text, nullable=True)  # e.g. {"21": 21, "10.5": 10.5}
    # Percepciones (Argentina)
    perception_enabled = Column(Boolean, default=False, nullable=False)
    perception_rates_json = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
