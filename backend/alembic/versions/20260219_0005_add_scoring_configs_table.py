"""add scoring configs table

Revision ID: 20260219_0005
Revises: 20260219_0004
Create Date: 2026-02-19 00:05:00.000000
"""

from datetime import datetime
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "20260219_0005"
down_revision = "20260219_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scoring_configs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("engine_name", sa.String(length=100), nullable=False),
        sa.Column("version", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("weights_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("thresholds_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(op.f("ix_scoring_configs_engine_name"), "scoring_configs", ["engine_name"], unique=False)
    op.create_index(op.f("ix_scoring_configs_version"), "scoring_configs", ["version"], unique=False)
    op.create_index(op.f("ix_scoring_configs_is_active"), "scoring_configs", ["is_active"], unique=False)

    scoring_configs = sa.table(
        "scoring_configs",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("created_at", sa.DateTime()),
        sa.column("updated_at", sa.DateTime()),
        sa.column("engine_name", sa.String(length=100)),
        sa.column("version", sa.String(length=50)),
        sa.column("is_active", sa.Boolean()),
        sa.column("weights_json", postgresql.JSONB(astext_type=sa.Text())),
        sa.column("thresholds_json", postgresql.JSONB(astext_type=sa.Text())),
        sa.column("notes", sa.String()),
    )

    now = datetime.utcnow()
    op.bulk_insert(
        scoring_configs,
        [
            {
                "id": uuid4(),
                "created_at": now,
                "updated_at": now,
                "engine_name": "journey_health",
                "version": "journey_health_v1",
                "is_active": True,
                "weights_json": {
                    "research_progress": 1.2,
                    "mental_wellbeing": 1.3,
                    "supervisor_relationship": 1.1,
                    "work_life_balance": 1.0,
                    "academic_confidence": 1.0,
                    "time_management": 0.9,
                    "motivation": 1.1,
                    "support_network": 1.0,
                },
                "thresholds_json": {
                    "excellent": 80.0,
                    "good": 65.0,
                    "fair": 50.0,
                    "concerning": 35.0,
                    "critical": 0.0,
                },
                "notes": "Initial journey health scoring config",
            },
            {
                "id": uuid4(),
                "created_at": now,
                "updated_at": now,
                "engine_name": "opportunity_relevance",
                "version": "opportunity_relevance_v1",
                "is_active": True,
                "weights_json": {
                    "discipline": 0.40,
                    "stage": 0.30,
                    "timeline": 0.15,
                    "deadline": 0.15,
                },
                "thresholds_json": {},
                "notes": "Initial opportunity relevance scoring config",
            },
        ],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_scoring_configs_is_active"), table_name="scoring_configs")
    op.drop_index(op.f("ix_scoring_configs_version"), table_name="scoring_configs")
    op.drop_index(op.f("ix_scoring_configs_engine_name"), table_name="scoring_configs")
    op.drop_table("scoring_configs")
