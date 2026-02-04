"""create transaction_events and fraud_predictions

Revision ID: a3913a2fe953
Revises:
Create Date: 2026-02-03 20:22:21.565308

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "a3913a2fe953"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "transaction_events",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("source", sa.String(length=64), nullable=False, server_default="api"),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("merchant_id", sa.String(length=64), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False, server_default="EUR"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_table(
        "fraud_predictions",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("event_id", sa.String(length=64), nullable=False),
        sa.Column("model_version", sa.String(length=32), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("decision", sa.String(length=16), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )


def downgrade() -> None:
    op.drop_table("fraud_predictions")
    op.drop_table("transaction_events")
