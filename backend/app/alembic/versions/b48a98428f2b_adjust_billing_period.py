"""adjust billing period

Revision ID: b48a98428f2b
Revises: 46754d1628dc
Create Date: 2022-04-25 18:04:37.035977

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = "b48a98428f2b"
down_revision = "46754d1628dc"
branch_labels = None
depends_on = None


def upgrade():
    billing_period = op.create_table(
        "billing_period",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("period", sa.String(), nullable=False, index=True, unique=True),
    )

    op.add_column(
        "billing",
        sa.Column("period_id", sa.Integer(), nullable=True),
    )

    op.execute(
        billing_period.insert().values(period=datetime.utcnow().strftime("%Y-%m"))
    )

    op.execute(
        sa.table("billing", sa.column("period_id"))
        .update()
        .values(period_id=sa.select([sa.func.max(billing_period.c.id)]).as_scalar())
    )

    op.alter_column("billing", "period_id", nullable=False)

    op.create_foreign_key(
        "fk_billing_period_id",
        "billing",
        "billing_period",
        ["period_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade():
    pass
