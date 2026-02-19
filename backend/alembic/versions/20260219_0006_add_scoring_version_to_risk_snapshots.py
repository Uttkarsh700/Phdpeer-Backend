"""add scoring version to risk snapshots

Revision ID: 20260219_0006
Revises: 20260219_0005
Create Date: 2026-02-19 00:06:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260219_0006"
down_revision = "20260219_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "risk_assessment_snapshots",
        sa.Column("scoring_version", sa.String(length=50), nullable=True),
    )

    op.execute(
        """
        UPDATE risk_assessment_snapshots
        SET scoring_version = config_version
        WHERE scoring_version IS NULL
        """
    )

    op.alter_column("risk_assessment_snapshots", "scoring_version", nullable=False)
    op.create_index(
        op.f("ix_risk_assessment_snapshots_scoring_version"),
        "risk_assessment_snapshots",
        ["scoring_version"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_risk_assessment_snapshots_scoring_version"), table_name="risk_assessment_snapshots")
    op.drop_column("risk_assessment_snapshots", "scoring_version")
