"""plans and subscriptions

Revision ID: 0002_plans_and_subscriptions
Revises: 0001_initial_saas_schema
Create Date: 2026-07-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_plans_and_subscriptions"
down_revision: str | None = "0001_initial_saas_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "plans",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("code", sa.String(), nullable=False, unique=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("monthly_message_limit", sa.Integer(), nullable=False),
        sa.Column("monthly_code_execution_limit", sa.Integer(), nullable=False),
        sa.Column("storage_bytes_limit", sa.BigInteger(), nullable=False),
        sa.Column("max_upload_file_bytes", sa.BigInteger(), nullable=False),
        sa.Column("price_cents", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_plans_code", "plans", ["code"])

    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=True),
        sa.Column("plan_code", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("provider_customer_id", sa.String(), nullable=True),
        sa.Column("provider_subscription_id", sa.String(), nullable=True),
        sa.Column("current_period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"])
    op.create_index("ix_subscriptions_organization_id", "subscriptions", ["organization_id"])
    op.create_index("ix_subscriptions_plan_code", "subscriptions", ["plan_code"])


def downgrade() -> None:
    op.drop_table("subscriptions")
    op.drop_table("plans")
