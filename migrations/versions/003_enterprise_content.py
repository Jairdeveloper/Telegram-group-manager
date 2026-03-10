"""Add enterprise content tables.

Revision ID: 003_enterprise_content
Revises: 002_enterprise_tables
Create Date: 2026-03-10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "003_enterprise_content"
down_revision: Union[str, None] = "002_enterprise_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "enterprise_rules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.String(255), nullable=False),
        sa.Column("chat_id", sa.BigInteger(), nullable=False),
        sa.Column("rules_text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_enterprise_rules_tenant_chat",
        "enterprise_rules",
        ["tenant_id", "chat_id"],
        unique=True,
    )
    op.create_index("ix_enterprise_rules_tenant_id", "enterprise_rules", ["tenant_id"])

    op.create_table(
        "enterprise_welcome",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.String(255), nullable=False),
        sa.Column("chat_id", sa.BigInteger(), nullable=False),
        sa.Column("welcome_text", sa.Text(), nullable=False),
        sa.Column("enabled", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_enterprise_welcome_tenant_chat",
        "enterprise_welcome",
        ["tenant_id", "chat_id"],
        unique=True,
    )
    op.create_index("ix_enterprise_welcome_tenant_id", "enterprise_welcome", ["tenant_id"])

    op.create_table(
        "enterprise_notes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.String(255), nullable=False),
        sa.Column("chat_id", sa.BigInteger(), nullable=False),
        sa.Column("note_key", sa.String(255), nullable=False),
        sa.Column("content_type", sa.String(50), nullable=False),
        sa.Column("content_text", sa.Text(), nullable=True),
        sa.Column("file_id", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_enterprise_notes_tenant_chat_key",
        "enterprise_notes",
        ["tenant_id", "chat_id", "note_key"],
        unique=True,
    )
    op.create_index("ix_enterprise_notes_tenant_id", "enterprise_notes", ["tenant_id"])

    op.create_table(
        "enterprise_filters",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.String(255), nullable=False),
        sa.Column("chat_id", sa.BigInteger(), nullable=False),
        sa.Column("pattern", sa.String(255), nullable=False),
        sa.Column("response_text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_enterprise_filters_tenant_chat_pattern",
        "enterprise_filters",
        ["tenant_id", "chat_id", "pattern"],
        unique=True,
    )
    op.create_index("ix_enterprise_filters_tenant_id", "enterprise_filters", ["tenant_id"])


def downgrade() -> None:
    op.drop_index("ix_enterprise_filters_tenant_id", table_name="enterprise_filters")
    op.drop_index("ix_enterprise_filters_tenant_chat_pattern", table_name="enterprise_filters")
    op.drop_table("enterprise_filters")
    op.drop_index("ix_enterprise_notes_tenant_id", table_name="enterprise_notes")
    op.drop_index("ix_enterprise_notes_tenant_chat_key", table_name="enterprise_notes")
    op.drop_table("enterprise_notes")
    op.drop_index("ix_enterprise_welcome_tenant_id", table_name="enterprise_welcome")
    op.drop_index("ix_enterprise_welcome_tenant_chat", table_name="enterprise_welcome")
    op.drop_table("enterprise_welcome")
    op.drop_index("ix_enterprise_rules_tenant_id", table_name="enterprise_rules")
    op.drop_index("ix_enterprise_rules_tenant_chat", table_name="enterprise_rules")
    op.drop_table("enterprise_rules")
