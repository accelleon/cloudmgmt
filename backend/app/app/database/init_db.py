from sqlalchemy.orm import Session

from app import schema, database
from app.core.config import configs

# Make sure all SQLAlchemy modules are import before initalizing DB
# otherwise SQLAlchemy might explode with relationships
from app.database import baseimport  # noqa


def init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations
    # but we have the option of creating the tables by uncommenting
    # Base.metadata.create_all(bind=engine)

    # Create our first user if it doesn't exist yet
    user = database.user.get_by_username(db, username=configs.FIRST_USER_NAME)
    if not user:
        user_in = schema.CreateUser(
            username=configs.FIRST_USER_NAME,
            password=configs.FIRST_USER_PASS,
            first_name="",
            last_name="",
            is_admin=True,
        )
        user = database.user.create(db, obj_in=user_in)
