"""add cloud metric table

Revision ID: 864ec63ffdbc
Revises: 7c59579cc8ad
Create Date: 2022-05-10 20:23:13.592607

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "864ec63ffdbc"
down_revision = "7c59579cc8ad"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "cloud_metric",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "account_id",
            sa.Integer,
            sa.ForeignKey("account.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("time", sa.DateTime, nullable=False),
        sa.Column("instances", sa.Integer, nullable=False),
        sa.Index("idx_cloud_metric_time", "time", postgresql_using="brin"),
        sa.UniqueConstraint("account_id", "time"),
    )


def downgrade():
    pass
