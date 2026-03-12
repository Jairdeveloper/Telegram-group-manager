"""Add enterprise moderation tables.

Revision ID: 004_enterprise_moderation
Revises: 003_enterprise_content
Create Date: 2026-03-10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "004_enterprise_moderation"
down_revision: Union[str, None] = "003_enterprise_content"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "enterprise_antispam",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.String(255), nullable=False),
        sa.Column("chat_id", sa.BigInteger(), nullable=False),
        sa.Column("enabled", sa.Integer(), nullable=True),
        sa.Column("spamwatch_enabled", sa.Integer(), nullable=True),
        sa.Column("sibyl_enabled", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_enterprise_antispam_tenant_chat",
        "enterprise_antispam",
        ["tenant_id", "chat_id"],
        unique=True,
    )
    op.create_index("ix_enterprise_antispam_tenant_id", "enterprise_antispam", ["tenant_id"])

    op.create_table(
        "enterprise_blacklist",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.String(255), nullable=False),
        sa.Column("chat_id", sa.BigInteger(), nullable=False),
        sa.Column("pattern", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_enterprise_blacklist_tenant_chat_pattern",
        "enterprise_blacklist",
        ["tenant_id", "chat_id", "pattern"],
        unique=True,
    )
    op.create_index("ix_enterprise_blacklist_tenant_id", "enterprise_blacklist", ["tenant_id"])

    op.create_table(
        "enterprise_sticker_blacklist",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.String(255), nullable=False),
        sa.Column("chat_id", sa.BigInteger(), nullable=False),
        sa.Column("sticker_file_id", sa.String(512), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_enterprise_sticker_blacklist_tenant_chat",
        "enterprise_sticker_blacklist",
        ["tenant_id", "chat_id", "sticker_file_id"],
        unique=True,
    )
    op.create_index(
        "ix_enterprise_sticker_blacklist_tenant_id",
        "enterprise_sticker_blacklist",
        ["tenant_id"],
    )

    op.create_table(
        "enterprise_antichannel",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.String(255), nullable=False),
        sa.Column("chat_id", sa.BigInteger(), nullable=False),
        sa.Column("enabled", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_enterprise_antichannel_tenant_chat",
        "enterprise_antichannel",
        ["tenant_id", "chat_id"],
        unique=True,
    )
    op.create_index("ix_enterprise_antichannel_tenant_id", "enterprise_antichannel", ["tenant_id"])


def downgrade() -> None:
    op.drop_index("ix_enterprise_antichannel_tenant_id", table_name="enterprise_antichannel")
    op.drop_index("ix_enterprise_antichannel_tenant_chat", table_name="enterprise_antichannel")
    op.drop_table("enterprise_antichannel")
    op.drop_index(
        "ix_enterprise_sticker_blacklist_tenant_id",
        table_name="enterprise_sticker_blacklist",
    )
    op.drop_index(
        "ix_enterprise_sticker_blacklist_tenant_chat",
        table_name="enterprise_sticker_blacklist",
    )
    op.drop_table("enterprise_sticker_blacklist")
    op.drop_index("ix_enterprise_blacklist_tenant_id", table_name="enterprise_blacklist")
    op.drop_index(
        "ix_enterprise_blacklist_tenant_chat_pattern",
        table_name="enterprise_blacklist",
    )
    op.drop_table("enterprise_blacklist")
    op.drop_index("ix_enterprise_antispam_tenant_id", table_name="enterprise_antispam")
    op.drop_index("ix_enterprise_antispam_tenant_chat", table_name="enterprise_antispam")
    op.drop_table("enterprise_antispam")
