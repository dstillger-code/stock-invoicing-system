"""Modelos del esquema business (productos, precios, inventario)."""
from sqlalchemy import Column, String, Text, Numeric, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.base import Base


class Country(Base):
    """País con configuración de impuestos."""

    __tablename__ = "countries"
    __table_args__ = {"schema": "business"}

    code = Column(String(2), primary_key=True)
    name = Column(Text, nullable=False)
    currency_code = Column(String(3), nullable=True)
    default_tax_rate = Column(Numeric(5, 2), nullable=True)

    precios = relationship("ProductPrice", back_populates="country")


class Product(Base):
    """Producto en el catálogo."""

    __tablename__ = "products"
    __table_args__ = {"schema": "business"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    precios = relationship("ProductPrice", back_populates="product", cascade="all, delete-orphan")
    inventory = relationship("Inventory", back_populates="product", uselist=False, cascade="all, delete-orphan")


class ProductPrice(Base):
    """Precio por país con configuración de IVA."""

    __tablename__ = "product_prices"
    __table_args__ = (
        UniqueConstraint("product_id", "country_code", name="uq_product_country"),
        {"schema": "business"},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("business.products.id", ondelete="CASCADE"), nullable=False)
    country_code = Column(String(2), ForeignKey("business.countries.code"), nullable=False)
    net_price = Column(Numeric(12, 2), nullable=False)
    tax_rate = Column(Numeric(5, 2), nullable=False)
    is_exempt = Column(Boolean, default=False, nullable=False)

    product = relationship("Product", back_populates="precios")
    country = relationship("Country", back_populates="precios")


class Inventory(Base):
    """Inventario de productos."""

    __tablename__ = "inventory"
    __table_args__ = {"schema": "business"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("business.products.id", ondelete="CASCADE"), unique=True, nullable=False)
    quantity = Column(Numeric(12, 0), default=0, nullable=False)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    product = relationship("Product", back_populates="inventory")
