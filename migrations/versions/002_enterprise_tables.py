"""Add enterprise user and ban tables.

Revision ID: 002_enterprise_tables
Revises: 001_initial
Create Date: 2026-03-10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "002_enterprise_tables"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "enterprise_users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.String(255), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_enterprise_users_tenant_user",
        "enterprise_users",
        ["tenant_id", "user_id"],
        unique=True,
    )
    op.create_index("ix_enterprise_users_tenant_id", "enterprise_users", ["tenant_id"])

    op.create_table(
        "enterprise_bans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.String(255), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("banned_by", sa.BigInteger(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_enterprise_bans_tenant_user",
        "enterprise_bans",
        ["tenant_id", "user_id"],
        unique=True,
    )
    op.create_index("ix_enterprise_bans_tenant_id", "enterprise_bans", ["tenant_id"])


def downgrade() -> None:
    op.drop_index("ix_enterprise_bans_tenant_id", table_name="enterprise_bans")
    op.drop_index("ix_enterprise_bans_tenant_user", table_name="enterprise_bans")
    op.drop_table("enterprise_bans")
    op.drop_index("ix_enterprise_users_tenant_id", table_name="enterprise_users")
    op.drop_index("ix_enterprise_users_tenant_user", table_name="enterprise_users")
    op.drop_table("enterprise_users")
