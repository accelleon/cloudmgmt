"""create billing export templates

Revision ID: f1db215bfa62
Revises: 85312f770e10
Create Date: 2022-04-20 18:50:23.914599

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1db215bfa62'
down_revision = '85312f770e10'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'template',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False, unique=True),
        sa.Column('description', sa.String, nullable=False),
    )

    op.create_table(
        'template_order',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('template_id', sa.Integer, sa.ForeignKey('template.id', ondelete="CASCADE"), index=True, nullable=False),
        sa.Column('account_id', sa.Integer, sa.ForeignKey('account.id', ondelete="CASCADE"), nullable=False),
        sa.Column('sort_order', sa.Integer, nullable=False),

        sa.UniqueConstraint('template_id', 'account_id'),
    )


def downgrade():
    pass
