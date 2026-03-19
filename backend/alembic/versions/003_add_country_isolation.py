"""add country isolation to users and products

Revision ID: 003_add_country_isolation
Revises: 002_add_products_is_active
Create Date: 2026-03-19 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "003_add_country_isolation"
down_revision: Union[str, Sequence[str], None] = "002_add_products_is_active"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users: add country_code with default CL
    op.add_column("users", sa.Column("country_code", sa.String(2), nullable=False, server_default="CL"), schema="auth")
    op.create_unique_constraint("uq_user_email_country", "users", ["email", "country_code"], schema="auth")
    op.drop_index("ix_auth_users_email", table_name="users", schema="auth")

    # Products: add country_code with default CL, make sku non-unique
    op.add_column("products", sa.Column("country_code", sa.String(2), nullable=False, server_default="CL"), schema="business")
    op.create_unique_constraint("uq_product_sku_country", "products", ["sku", "country_code"], schema="business")

    # Product prices: drop country_code, tax_rate, is_exempt columns
    op.drop_column("product_prices", "country_code", schema="business")
    op.drop_column("product_prices", "tax_rate", schema="business")
    op.drop_column("product_prices", "is_exempt", schema="business")


def downgrade() -> None:
    op.add_column("product_prices", sa.Column("is_exempt", sa.Boolean(), nullable=False, server_default="false"), schema="business")
    op.add_column("product_prices", sa.Column("tax_rate", sa.Numeric(5, 2), nullable=False, server_default="19.00"), schema="business")
    op.add_column("product_prices", sa.Column("country_code", sa.String(2), nullable=False, server_default="CL"), schema="business")
    op.drop_constraint("uq_product_sku_country", "products", schema="business")
    op.drop_column("products", "country_code", schema="business")
    op.create_index("ix_auth_users_email", "users", ["email"], unique=True, schema="auth")
    op.drop_constraint("uq_user_email_country", "users", schema="auth")
    op.drop_column("users", "country_code", schema="auth")
