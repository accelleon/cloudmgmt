"""create account table

Revision ID: ce92ba97b359
Revises: 0b0f2514c56b
Create Date: 2022-04-07 15:53:39.686501

"""
from alembic import op
import sqlalchemy as sa


from app.model.iaas import IaasType


# revision identifiers, used by Alembic.
revision = "ce92ba97b359"
down_revision = "0b0f2514c56b"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "iaas",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, index=True, unique=True, nullable=False),
        sa.Column("type", sa.Enum(IaasType), nullable=False),
        sa.Column("params", sa.JSON, nullable=False),
    )

    op.create_table(
        "account",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, index=True, nullable=False),
        sa.Column("iaas_id", sa.Integer, sa.ForeignKey("iaas.id"), nullable=False),
        sa.Column("data", sa.JSON, nullable=False),
        sa.Index("iaas_id", "name", unique=True),
    )


def downgrade():
    pass
