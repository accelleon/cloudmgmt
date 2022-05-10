"""cloud error handling

Revision ID: b7f69c234e17
Revises: 120ab9341a2f
Create Date: 2022-05-05 20:38:21.369006

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7f69c234e17'
down_revision = '120ab9341a2f'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("account", sa.Column("validated", sa.Boolean(), nullable=True, default=False))
    op.execute(
        sa.table("account", sa.Column("validated")).update().values(validated=False)
    )
    op.alter_column("account", "validated", nullable=False)

    op.add_column("account", sa.Column("last_error", sa.String(), nullable=True))


def downgrade():
    pass
