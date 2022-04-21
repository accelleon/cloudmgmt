"""template trigger

Revision ID: 46754d1628dc
Revises: f1db215bfa62
Create Date: 2022-04-21 18:20:20.911506

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "46754d1628dc"
down_revision = "f1db215bfa62"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
CREATE FUNCTION update_template_trigger() RETURNS trigger AS $$
BEGIN
    WITH templates AS (
        SELECT t.id AS id, count(tmp.id) AS order_count
        FROM template t
        LEFT JOIN template_order tmp ON tmp.template_id = t.id
        GROUP BY t.id
    )
    INSERT INTO template_order (template_id, account_id, sort_order)
    SELECT t.id, NEW.id, t.order_count
    from templates t;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""
    )

    op.execute(
        """
CREATE TRIGGER update_template_trigger
AFTER INSERT ON account
FOR EACH ROW EXECUTE PROCEDURE update_template_trigger();
"""
    )


def downgrade():
    pass
