from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import registry

from api.settings import Settings

table_registry = registry()

engine = create_async_engine(Settings().DATABASE_URL)


async def get_session() -> AsyncGenerator[AsyncSession]:  # pragma no cover
    async with AsyncSession(engine) as session:
        yield session
