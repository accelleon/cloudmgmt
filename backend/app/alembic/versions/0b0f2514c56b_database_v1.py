"""Database v1

Revision ID: 0b0f2514c56b
Revises: mypy
Create Date: 2022-03-14 23:40:48.550109

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0b0f2514c56b"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():

    op.create_table(
        "user",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String, index=True, unique=True, nullable=False),
        sa.Column("password", sa.String, nullable=False),
        sa.Column("first_name", sa.String, nullable=False),
        sa.Column("last_name", sa.String, nullable=False),
        sa.Column("is_admin", sa.Boolean, server_default="False", nullable=False),
        sa.Column("twofa_enabled", sa.Boolean, server_default="False", nullable=False),
        sa.Column("twofa_secret", sa.String, nullable=True),
        sa.Column("twofa_secret_tmp", sa.String, nullable=True),
    )


def downgrade():

    pass
