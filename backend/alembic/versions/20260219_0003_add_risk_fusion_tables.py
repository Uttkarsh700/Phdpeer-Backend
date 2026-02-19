"""add risk fusion tables

Revision ID: 20260219_0003
Revises: 20260219_0002
Create Date: 2026-02-19 00:03:00.000000
"""

from uuid import uuid4
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "20260219_0003"
down_revision = "20260219_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "risk_weight_configs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("version", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("weights_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("thresholds_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_risk_weight_configs_version"), "risk_weight_configs", ["version"], unique=True)
    op.create_index(op.f("ix_risk_weight_configs_is_active"), "risk_weight_configs", ["is_active"], unique=False)

    op.create_table(
        "risk_assessment_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("timeline_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("config_version", sa.String(length=50), nullable=False),
        sa.Column("composite_score", sa.Float(), nullable=False),
        sa.Column("risk_level", sa.String(length=20), nullable=False),
        sa.Column("contributing_signals", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("threshold_breaches", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("weight_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("input_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(["timeline_id"], ["committed_timelines.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_risk_assessment_snapshots_user_id"), "risk_assessment_snapshots", ["user_id"], unique=False)
    op.create_index(op.f("ix_risk_assessment_snapshots_timeline_id"), "risk_assessment_snapshots", ["timeline_id"], unique=False)
    op.create_index(op.f("ix_risk_assessment_snapshots_config_version"), "risk_assessment_snapshots", ["config_version"], unique=False)
    op.create_index(op.f("ix_risk_assessment_snapshots_risk_level"), "risk_assessment_snapshots", ["risk_level"], unique=False)

    risk_weight_configs = sa.table(
        "risk_weight_configs",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("created_at", sa.DateTime()),
        sa.column("updated_at", sa.DateTime()),
        sa.column("version", sa.String(length=50)),
        sa.column("is_active", sa.Boolean()),
        sa.column("weights_json", postgresql.JSONB(astext_type=sa.Text())),
        sa.column("thresholds_json", postgresql.JSONB(astext_type=sa.Text())),
        sa.column("notes", sa.String()),
    )

    op.bulk_insert(
        risk_weight_configs,
        [
            {
                "id": uuid4(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "version": "risk_fusion_v1",
                "is_active": True,
                "weights_json": {
                    "timeline_status": 0.35,
                    "health_score": 0.30,
                    "overdue_ratio": 0.20,
                    "supervision_latency": 0.15,
                },
                "thresholds_json": {
                    "overdue_ratio_delayed": 0.20,
                    "health_low": 50.0,
                    "supervision_latency_high": 30.0,
                    "risk_level_medium": 45.0,
                    "risk_level_high": 70.0,
                    "supervision_latency_max": 60.0,
                },
                "notes": "Default risk fusion config",
            }
        ],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_risk_assessment_snapshots_risk_level"), table_name="risk_assessment_snapshots")
    op.drop_index(op.f("ix_risk_assessment_snapshots_config_version"), table_name="risk_assessment_snapshots")
    op.drop_index(op.f("ix_risk_assessment_snapshots_timeline_id"), table_name="risk_assessment_snapshots")
    op.drop_index(op.f("ix_risk_assessment_snapshots_user_id"), table_name="risk_assessment_snapshots")
    op.drop_table("risk_assessment_snapshots")

    op.drop_index(op.f("ix_risk_weight_configs_is_active"), table_name="risk_weight_configs")
    op.drop_index(op.f("ix_risk_weight_configs_version"), table_name="risk_weight_configs")
    op.drop_table("risk_weight_configs")
