from datetime import datetime

import pytest
from sqlalchemy import select

from api.exceptions.base import ForbiddenError
from api.exceptions.chat_session import ChatSessionNotFoundError
from api.models.chat_session import ChatSession
from api.models.message import Message
from api.services.chat_session import ChatSessionsService
from tests.factories import ChatSessionFactory


@pytest.mark.asyncio
async def test_create_chat_session_success(
    session, mock_permission_checker, project, user
):
    service = ChatSessionsService(session, mock_permission_checker)

    chat = await service.create_chat_session(
        project_id=project.id, user_id=user.id, title='Chat de Design'
    )

    assert chat.title == 'Chat de Design'


@pytest.mark.asyncio
async def test_create_chat_session_forbidden(
    session, mock_permission_checker, project, user
):
    mock_permission_checker.has_permission.return_value = False
    service = ChatSessionsService(session, mock_permission_checker)

    with pytest.raises(ForbiddenError):
        await service.create_chat_session(
            project_id=project.id, user_id=user.id, title='Chat Proibido'
        )


@pytest.mark.asyncio
async def test_delete_chat_session_success(
    session, mock_permission_checker, chat_session, user
):
    service = ChatSessionsService(session, mock_permission_checker)

    await service.delete_chat_session(
        chat_id=chat_session.id, requester_id=user.id
    )

    db_chat = await session.scalar(
        select(ChatSession).where(ChatSession.id == chat_session.id)
    )
    assert db_chat is None


@pytest.mark.asyncio
async def test_delete_chat_session_not_found(session, mock_permission_checker):
    service = ChatSessionsService(session, mock_permission_checker)

    with pytest.raises(ChatSessionNotFoundError):
        await service.delete_chat_session(chat_id=999, requester_id=1)


@pytest.mark.asyncio
async def test_delete_chat_session_forbidden(
    session, mock_permission_checker, chat_session, user
):
    mock_permission_checker.has_permission.return_value = False
    service = ChatSessionsService(session, mock_permission_checker)

    with pytest.raises(ForbiddenError):
        await service.delete_chat_session(
            chat_id=chat_session.id, requester_id=user.id
        )


@pytest.mark.asyncio
async def test_update_chat_session_success(
    session, mock_permission_checker, chat_session, user
):
    service = ChatSessionsService(session, mock_permission_checker)

    updated = await service.update_chat_session(
        chat_id=chat_session.id, requester_id=user.id, title='Título Atualizado'
    )

    assert updated.title == 'Título Atualizado'


@pytest.mark.asyncio
async def test_update_chat_session_not_found(session, mock_permission_checker):
    service = ChatSessionsService(session, mock_permission_checker)

    with pytest.raises(ChatSessionNotFoundError):
        await service.update_chat_session(
            chat_id=999, requester_id=1, title='Novo'
        )


@pytest.mark.asyncio
async def test_update_chat_session_forbidden(
    session, mock_permission_checker, chat_session, user
):
    mock_permission_checker.has_permission.return_value = False
    service = ChatSessionsService(session, mock_permission_checker)

    with pytest.raises(ForbiddenError):
        await service.update_chat_session(
            chat_id=chat_session.id, requester_id=user.id, title='Novo'
        )


@pytest.mark.asyncio
async def test_update_chat_session_ignores_restricted_fields(
    session, mock_permission_checker, chat_session, user
):
    service = ChatSessionsService(session, mock_permission_checker)
    original_project_id = chat_session.project_id

    updated = await service.update_chat_session(
        chat_id=chat_session.id,
        requester_id=user.id,
        id=999,
        project_id=888,
        created_by=777,
        title='Apenas o título muda',
    )

    assert updated.project_id == original_project_id


@pytest.mark.asyncio
async def test_get_chats_by_project_success_all(
    session, mock_permission_checker, chat_session, project
):
    service = ChatSessionsService(session, mock_permission_checker)

    chats = await service.get_chats_by_project(
        project_id=project.id,
        title=None,
        cursor_date=None,
        cursor_id=None,
        limit=10,
    )

    assert len(chats) == 1


@pytest.mark.asyncio
async def test_get_chats_by_project_filter_by_title(
    session, mock_permission_checker, project, user
):
    service = ChatSessionsService(session, mock_permission_checker)
    chat = ChatSessionFactory(
        project_id=project.id,
        started_by=user.id,
        title='Design de Agent',
    )
    session.add(chat)
    await session.commit()

    chats = await service.get_chats_by_project(
        project_id=project.id,
        title='DeSiGn',
        cursor_date=None,
        cursor_id=None,
        limit=5,
    )

    assert chats[0].id == chat.id


@pytest.mark.asyncio
async def test_get_chats_by_project_with_cursor(
    session, mock_permission_checker, project, user, mock_db_time
):
    service = ChatSessionsService(session, mock_permission_checker)

    with mock_db_time(model=ChatSession, time=datetime(2026, 1, 2)):
        chat_novo = ChatSessionFactory(
            project_id=project.id, started_by=user.id
        )
        session.add(chat_novo)
        await session.commit()

    with mock_db_time(model=ChatSession, time=datetime(2026, 1, 1)):
        chat_antigo = ChatSessionFactory(
            project_id=project.id, started_by=user.id
        )
        session.add(chat_antigo)
        await session.commit()

    resultado = await service.get_chats_by_project(
        project_id=project.id,
        title=None,
        cursor_date=datetime(2026, 1, 2),
        cursor_id=chat_novo.id,
        limit=1,
    )

    assert resultado[0].id == chat_antigo.id


@pytest.mark.asyncio
async def test_get_chat_messages_success(
    session, mock_permission_checker, chat_session, project, user
):
    service = ChatSessionsService(session, mock_permission_checker)
    msg = Message(
        chat_session_id=chat_session.id,
        content='Olá',
    )

    msg.sender_type = Message.SenderType.USER
    msg.sender_user_id = user.id

    session.add(msg)
    await session.commit()

    messages = await service.get_chat_messages(
        chat_id=chat_session.id, project_id=project.id, requester_id=user.id
    )

    assert len(messages) == 1


@pytest.mark.asyncio
async def test_get_chat_messages_forbidden(
    session, mock_permission_checker, chat_session, project, user
):
    mock_permission_checker.has_permission.return_value = False
    service = ChatSessionsService(session, mock_permission_checker)

    with pytest.raises(ForbiddenError):
        await service.get_chat_messages(
            chat_id=chat_session.id, project_id=project.id, requester_id=user.id
        )


@pytest.mark.asyncio
async def test_save_message_sender_user_success(
    session, mock_permission_checker, chat_session, user
):
    service = ChatSessionsService(session, mock_permission_checker)

    msg = await service.save_message(
        chat_id=chat_session.id,
        content='Minha pergunta',
        type_sender='USER',
        sender_id=user.id,
    )

    assert msg.sender_user_id == user.id


@pytest.mark.asyncio
async def test_save_message_sender_ai_success(
    session, mock_permission_checker, chat_session, ai_agent
):
    service = ChatSessionsService(session, mock_permission_checker)

    msg = await service.save_message(
        chat_id=chat_session.id,
        content='Resposta do Bot',
        type_sender='AI',
        sender_id=ai_agent.id,
    )

    assert msg.sender_ai_id == ai_agent.id
