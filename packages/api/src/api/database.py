from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import registry

from api.settings import Settings

table_registry = registry()

engine = create_async_engine(Settings().DATABASE_URL)
Session = async_sessionmaker(bind=engine)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Gera uma sessão asyncrona."""
    async with Session() as session:
        yield session
