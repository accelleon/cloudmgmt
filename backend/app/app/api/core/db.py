from typing import AsyncIterable

from sqlalchemy.ext.asyncio import AsyncSession as Session

from app.core.config import configs
from app.database.session import SessionLocal


# Depend on a DB connection for an endpoint
async def get_db() -> AsyncIterable[Session]:
    async with SessionLocal() as session:
        yield session
