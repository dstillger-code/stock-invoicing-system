"""Modelos del esquema negocio (productos y precios por región)."""
from sqlalchemy import Column, String, Text, Integer, Numeric, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.base import Base


class Producto(Base):
    """Producto en esquema negocio."""

    __tablename__ = "productos"
    __table_args__ = {"schema": "negocio"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sku = Column(String(50), unique=True, index=True, nullable=False)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    categoria = Column(String(100), nullable=True)
    is_active = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    precios = relationship("PrecioPorRegion", back_populates="producto", cascade="all, delete-orphan")


class PrecioPorRegion(Base):
    """Precio por región con tipo de IVA configurable."""

    __tablename__ = "precios_por_region"
    __table_args__ = {"schema": "negocio"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    producto_id = Column(Integer, ForeignKey("negocio.productos.id", ondelete="CASCADE"), nullable=False)
    region = Column(String(10), nullable=False)
    precio_neto = Column(Numeric(12, 2), nullable=False)
    tipo_iva = Column(Numeric(5, 2), nullable=False)
    observaciones = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    producto = relationship("Producto", back_populates="precios")
