"""rename subscription tier pro to team

Revision ID: 20260219_0002
Revises: 20260219_0001
Create Date: 2026-02-19 00:02:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260219_0002"
down_revision = "20260219_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()

    if bind.dialect.name == "postgresql":
        op.execute("ALTER TYPE subscription_tier RENAME VALUE 'pro' TO 'team';")
    else:
        op.execute(
            sa.text(
                "UPDATE users SET subscription_tier = 'team' WHERE subscription_tier = 'pro'"
            )
        )


def downgrade() -> None:
    bind = op.get_bind()

    if bind.dialect.name == "postgresql":
        op.execute("ALTER TYPE subscription_tier RENAME VALUE 'team' TO 'pro';")
    else:
        op.execute(
            sa.text(
                "UPDATE users SET subscription_tier = 'pro' WHERE subscription_tier = 'team'"
            )
        )
