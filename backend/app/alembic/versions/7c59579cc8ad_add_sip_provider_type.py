"""add SIP provider type

Revision ID: 7c59579cc8ad
Revises: b7f69c234e17
Create Date: 2022-05-10 14:22:01.360320

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7c59579cc8ad"
down_revision = "b7f69c234e17"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE iaastype ADD VALUE 'SIP';")


def downgrade():
    pass
