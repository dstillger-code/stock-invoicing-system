"""Modelos del esquema stock (inventario)."""
from sqlalchemy import Column, String, Integer, Numeric, DateTime
from sqlalchemy.sql import func

from app.core.base import Base


class StockItem(Base):
    """
    Ítem de stock: id, sku, nombre, cantidad, precio_base.
    Esquema stock (separado de auth).
    """

    __tablename__ = "stock_items"
    __table_args__ = {"schema": "stock"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sku = Column(String(64), unique=True, index=True, nullable=False)
    nombre = Column(String(255), nullable=False)
    cantidad = Column(Integer, default=0, nullable=False)
    precio_base = Column(Numeric(14, 2), default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
