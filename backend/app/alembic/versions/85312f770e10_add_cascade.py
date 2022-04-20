"""Add cascade

Revision ID: 85312f770e10
Revises: 36cfccd5f11d
Create Date: 2022-04-20 14:00:22.422154

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "85312f770e10"
down_revision = "36cfccd5f11d"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("billing_account_id_fkey", "billing", type_="foreignkey")
    op.create_foreign_key(
        "billing_account_id_fkey",
        "billing",
        "account",
        ["account_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade():
    pass
