"""add currency to reporting

Revision ID: 36cfccd5f11d
Revises: b11daad9366d
Create Date: 2022-04-18 15:49:10.349429

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "36cfccd5f11d"
down_revision = "b11daad9366d"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "account",
        sa.Column("currency", sa.String(length=3), nullable=True, default="USD"),
    )
    currency = sa.table("account", sa.column("currency"))
    op.execute(currency.update().values(currency="USD"))
    op.alter_column("account", "currency", nullable=False)


def downgrade():
    pass
