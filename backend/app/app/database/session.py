from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import configs

engine = create_async_engine(
    configs.DATABASE_URI,
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
