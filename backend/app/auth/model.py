"""Modelos del esquema auth (usuarios, sesiones)."""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ARRAY, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.base import Base


class User(Base):
    """Usuario en esquema auth."""

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", "country_code", name="uq_user_email_country"),
        {"schema": "auth"},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), default="operator", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    allowed_modules = Column(ARRAY(String), default=["stock"], nullable=False)
    password_changed = Column(Boolean, default=False, nullable=False)
    expiration_days = Column(Integer, default=30, nullable=False)
    country_code = Column(String(2), nullable=False, default="CL")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
