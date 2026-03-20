"""Add company_settings table."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "004_add_company_settings"
down_revision = "003_add_country_isolation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS business")
    op.create_table(
        "company_settings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("country_code", sa.String(2), sa.Nullable(False), unique=True),
        sa.Column("company_name", sa.Text(), sa.Nullable(False), server_default="Mi Empresa"),
        sa.Column("logo_url", sa.Text(), sa.Nullable(True)),
        sa.Column("tax_id", sa.String(50), sa.Nullable(True)),
        sa.Column("address", sa.Text(), sa.Nullable(True)),
        sa.Column("phone", sa.String(30), sa.Nullable(True)),
        sa.Column("email", sa.String(255), sa.Nullable(True)),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            onupdate=sa.text("now()"),
        ),
        schema="business",
    )


def downgrade() -> None:
    op.drop_table("company_settings", schema="business")
