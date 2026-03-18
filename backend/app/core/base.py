"""Base para modelos SQLAlchemy (compartida entre esquemas)."""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base declarativa para todos los modelos."""

    pass
