from unittest.mock import AsyncMock

import pytest

from api.services.permission import PermissionCheckerService


@pytest.mark.asyncio
async def test_has_permission_returns_true_when_record_exists():
    mock_session = AsyncMock()
    service = PermissionCheckerService(session=mock_session)

    mock_session.scalar.return_value = 1

    result = await service.has_permission(
        project_id=10, member_id=5, permission='chat:create'
    )

    assert result is True


@pytest.mark.asyncio
async def test_has_permission_returns_false_when_record_does_not_exist():
    mock_session = AsyncMock()
    service = PermissionCheckerService(session=mock_session)

    mock_session.scalar.return_value = None

    result = await service.has_permission(
        project_id=10, member_id=5, permission='não_existe'
    )

    assert result is False
