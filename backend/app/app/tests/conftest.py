from typing import Dict, AsyncIterable, Iterable

import pytest
import asyncio
from httpx import AsyncClient
from asyncio import AbstractEventLoop
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession as Session

from app.database.session import engine, SessionLocal
from app.api_main import app
from app.tests.utils.user import auth_headers_random, admin_user_headers


@pytest.fixture(scope="session")
def event_loop() -> Iterable[AbstractEventLoop]:
    policy = asyncio.get_event_loop_policy()
    loop = policy.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def fastapi_app() -> FastAPI:
    return app


@pytest.fixture(scope="session")
async def client(fastapi_app: FastAPI) -> AsyncIterable[AsyncClient]:
    async with AsyncClient(
        app=fastapi_app,
        base_url="http://localhost:8000",
    ) as client:
        yield client


@pytest.fixture(scope="session")
async def db() -> AsyncIterable[Session]:
    async with engine.connect() as conn:
        transaction = await conn.begin()
        SessionLocal.configure(bind=conn)

        async with SessionLocal() as session:
            yield session

        if transaction.is_active:
            await transaction.rollback()


@pytest.fixture(scope="module")
async def admin_token_headers(client: AsyncClient) -> Dict[str, str]:
    return await admin_user_headers(client=client)


@pytest.fixture(scope="module")
async def user_token_headers(client: AsyncClient, db: Session) -> Dict[str, str]:
    return await auth_headers_random(client=client, db=db)


@pytest.fixture(scope="session")
def celery_config():
    return {"broker_url": "redis://", "result_backend": "redis://"}
