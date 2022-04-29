from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import aioredis

from app.core.config import configs

engine = create_async_engine(
    configs.POSTGRES_DSN,
    future=True,
    pool_size=20,
    pool_pre_ping=True,
    pool_use_lifo=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    future=True,
    class_=AsyncSession,  # type: ignore
    expire_on_commit=False,
)

redis_2fa = aioredis.from_url(
    configs.REDIS_DSN, db=configs.REDIS_2FA_DB, encoding="utf-8", decode_responses=True
)
