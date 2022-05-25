"""user teams and account groups

Revision ID: 8a101c6501f3
Revises: 864ec63ffdbc
Create Date: 2022-05-23 12:14:54.276564

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8a101c6501f3"
down_revision = "864ec63ffdbc"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "groups",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), index=True, unique=True),
    )

    op.add_column(
        "account",
        sa.Column("group_id", sa.Integer, sa.ForeignKey("groups.id"), nullable=True),
    )

    op.execute("INSERT INTO groups (name) VALUES ('change-me');")
    op.execute("UPDATE account SET group_id = 0;")

    op.alter_column("account", "group_id", nullable=False)


def downgrade():
    pass
