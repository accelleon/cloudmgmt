from sqlalchemy.ext.asyncio import AsyncSession as Session

from app import database, model
from app.core.config import configs
from pycloud import CloudFactory

# Make sure all SQLAlchemy modules are import before initalizing DB
# otherwise SQLAlchemy might explode with relationships
from app.database import baseimport  # noqa


async def init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations
    # but we have the option of creating the tables by uncommenting
    # Base.metadata.create_all(bind=engine)

    # Create our first user if it doesn't exist yet
    user = await database.user.get_by_username(db, username=configs.FIRST_USER_NAME)
    if not user:
        user_in = model.CreateUser(
            username=configs.FIRST_USER_NAME,
            password=configs.FIRST_USER_PASS,
            first_name="",
            last_name="",
            is_admin=True,
        )
        user = await database.user.create(db, obj_in=user_in)

    iaasFactory = CloudFactory.get_providers()
    for provider in iaasFactory:
        if iaas := await database.iaas.get_by_name(db, name=provider.name):
            await database.iaas.update(db, db_obj=iaas, obj_in=provider)
            continue
        await database.iaas.create(db, obj_in=provider)

    if not await database.template.get_by_name(db, name="default"):
        accounts = await database.account.get_all(db)
        account_ids = [account.id for account in accounts]
        template_in = model.CreateTemplate(
            name="default",
            description="Default template",
            order=account_ids,
        )
        await database.template.create(db, obj_in=template_in)
