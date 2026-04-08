from contextlib import contextmanager
from datetime import datetime
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from api.app import app
from api.database import table_registry
from api.dependecies import get_user_service
from api.security import get_password_hash
from api.services.user import UserService
from api.settings import Settings
from tests.factories import UserFactory


@pytest.fixture(scope='session')
def engine():
    return create_async_engine(Settings().DATABASE_URL)


@pytest_asyncio.fixture
async def session(engine):
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@contextmanager
def _mock_db_time(*, model, time=datetime(2026, 1, 1)):
    def fake_time_handler(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_handler)

    yield time

    event.remove(model, 'before_insert', fake_time_handler)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest_asyncio.fixture
async def user(session):
    user = UserFactory(
        password=get_password_hash('senha'),
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


@pytest_asyncio.fixture
async def other_user(session):
    user = UserFactory(
        password=get_password_hash('senha'),
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


@pytest.fixture
def password_hash_patch(monkeypatch):
    monkeypatch.setattr('api.services.user.get_password_hash', lambda p: p)


@pytest.fixture
def user_service_mock():
    mock = AsyncMock(spec=UserService)
    return mock


@pytest.fixture
def client(user_service_mock):
    app.dependency_overrides[get_user_service] = lambda: user_service_mock

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
