"""Add billing table

Revision ID: b11daad9366d
Revises: ce92ba97b359
Create Date: 2022-04-13 19:52:47.977925

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b11daad9366d"
down_revision = "ce92ba97b359"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "billing",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "account_id", sa.Integer, sa.ForeignKey("account.id"), nullable=False
        ),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("total", sa.Float, nullable=False),
        sa.Column("balance", sa.Float, nullable=True),
        sa.Index("idx_billing_end_date", "end_date", postgresql_using="brin"),
        sa.UniqueConstraint("account_id", "start_date", "end_date"),
    )


def downgrade():
    pass
