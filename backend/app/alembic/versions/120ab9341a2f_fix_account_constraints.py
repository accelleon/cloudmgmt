"""fix account constraints

Revision ID: 120ab9341a2f
Revises: b48a98428f2b
Create Date: 2022-05-05 17:15:35.812834

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "120ab9341a2f"
down_revision = "b48a98428f2b"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index("iaas_id")
    op.drop_index("ix_account_name")

    op.create_index(
        "ix_account_name_iaas",
        "account",
        ["name", "iaas_id"],
        unique=True,
    )


def downgrade():
    pass
