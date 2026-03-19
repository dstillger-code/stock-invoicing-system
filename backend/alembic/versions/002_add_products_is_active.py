"""add is_active column to products table

Revision ID: 002_add_products_is_active
Revises: 001_initial
Create Date: 2026-03-19 11:20:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "002_add_products_is_active"
down_revision: Union[str, Sequence[str], None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "products",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        schema="business",
    )


def downgrade() -> None:
    op.drop_column("products", "is_active", schema="business")
