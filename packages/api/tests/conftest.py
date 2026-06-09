from contextlib import contextmanager
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from api.app import app
from api.database import table_registry
from api.dependecies import get_auth_service, get_user_service
from api.security import get_password_hash
from api.services.auth import AuthService
from api.services.user import UserService
from api.settings import Settings
from tests.factories import (
    AiAgentFactory,
    ChatSessionFactory,
    PermissionFactory,
    ProjectFactory,
    ProjectMembersFactory,
    RoleFactory,
    UserFactory,
)


@pytest.fixture(scope='session')
def engine():
    return create_async_engine(Settings().TEST_DATABASE_URL)


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
async def role(session):
    role = RoleFactory()
    session.add(role)
    await session.commit()
    await session.refresh(role)
    return role


@pytest_asyncio.fixture
async def permission(session):
    permission = PermissionFactory()
    session.add(permission)
    await session.commit()
    await session.refresh(permission)
    return permission


@pytest_asyncio.fixture
async def project(session, user):
    project = ProjectFactory(created_by=user.id)
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project


@pytest_asyncio.fixture
async def project_member(session, user, project, role):
    project_member = ProjectMembersFactory(
        user_id=user.id,
        project_id=project.id,
        role_id=role.id,
    )
    session.add(project_member)
    await session.commit()
    await session.refresh(project_member)
    return project_member


@pytest_asyncio.fixture
async def ai_agent(session):
    agent = AiAgentFactory()
    session.add(agent)
    await session.commit()
    await session.refresh(agent)
    return agent


@pytest_asyncio.fixture
async def chat_session(session, user, project):
    session_chat = ChatSessionFactory(started_by=user.id, project_id=project.id)
    session.add(session_chat)
    await session.commit()
    await session.refresh(session_chat)
    return session_chat


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
def mock_permission_checker():
    checker = AsyncMock()
    checker.has_permission.return_value = True
    return checker


@pytest.fixture
def client(user_service_mock, mock_auth_service):
    app.dependency_overrides[get_user_service] = lambda: user_service_mock
    app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def auth_service():
    return AuthService(
        secret_key='test_secret',
        algorithm='HS256',
        access_token_expire_minutes=5,
        refresh_token_expire_days=7,
    )


@pytest.fixture
def mock_auth_service():
    mock = MagicMock()
    return mock


@pytest.fixture
def mock_request():
    request = MagicMock(spec=Request)
    request.cookies = {}
    return request
