# This is just here for alembic
# Make sure all models are imported *before* alembic imports them
from app.database.base import Base
from app.database.user import User
