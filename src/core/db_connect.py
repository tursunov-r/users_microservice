from collections.abc import AsyncGenerator

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.settings import settings

engine = create_async_engine(
    url=settings.db_url,
    echo=False,
    poolclass=NullPool,
)

test_engine = create_async_engine(
    url=settings.test_db_url,
    echo=False,
    poolclass=NullPool,
)

async_session = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

async_test_session = async_sessionmaker(
    test_engine, expire_on_commit=False, class_=AsyncSession
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        async with session.begin():
            yield session


async def test_get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_test_session() as session:
        async with session.begin():
            yield session
