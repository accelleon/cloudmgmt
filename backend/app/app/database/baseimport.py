# This is just here for alembic
# Make sure all models are imported *before* alembic imports them
from app.database.base import Base  # noqa
from app.database.user import User  # noqa
from app.database.iaas import Iaas  # noqa
from app.database.account import Account  # noqa
from app.database.billing import Billing  # noqa
from app.database.template import Template  # noqa
from app.database.metric import CloudMetric  # noqa
