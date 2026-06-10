from contextlib import aclosing

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_session
from api.models.ai_agent import AiAgent
from api.models.chat_session import ChatSession
from api.models.message import Message
from api.models.permission import Permission
from api.models.project import Project
from api.models.project_members import ProjectMembers
from api.models.role import Role
from api.models.role_permissions import RolePermissions
from api.models.user import User


@pytest.mark.asyncio
async def test_get_session_yield_async_session():
    async with aclosing(get_session()) as gen:
        session = await anext(gen)
        assert isinstance(session, AsyncSession)


@pytest.mark.asyncio
async def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='João', email='joão@gmail.com', password='senha'
        )
        session.add(new_user)
        await session.commit()

    db_user = await session.scalar(select(User).where(User.username == 'João'))

    assert db_user is not None
    assert db_user.username == 'João'
    assert db_user.email == 'joão@gmail.com'
    assert db_user.created_at == time
    assert db_user.updated_at == time


@pytest.mark.asyncio
async def test_create_role(session, mock_db_time):
    with mock_db_time(model=Role) as time:
        new_role = Role(name='ADMIN')
        session.add(new_role)
        await session.commit()

    db_role = await session.scalar(select(Role).where(Role.name == 'ADMIN'))

    assert db_role is not None
    assert db_role.name == 'ADMIN'
    assert db_role.created_at == time
    assert db_role.updated_at == time


@pytest.mark.asyncio
async def test_create_permission(session, mock_db_time):
    with mock_db_time(model=Permission) as time:
        new_permission = Permission(name='edit_branding')
        session.add(new_permission)
        await session.commit()

    db_permission = await session.scalar(
        select(Permission).where(Permission.name == 'edit_branding')
    )

    assert db_permission is not None
    assert db_permission.name == 'edit_branding'
    assert db_permission.created_at == time
    assert db_permission.updated_at == time


@pytest.mark.asyncio
async def test_create_role_permissions(session, mock_db_time, role, permission):
    with mock_db_time(model=RolePermissions) as time:
        association = RolePermissions(
            role_id=role.id, permission_id=permission.id
        )
        session.add(association)
        await session.commit()

    db_association = await session.scalar(
        select(RolePermissions).where(
            RolePermissions.role_id == role.id,
            RolePermissions.permission_id == permission.id,
        )
    )

    assert db_association is not None
    assert db_association.role_id == role.id
    assert db_association.permission_id == permission.id
    assert db_association.created_at == time
    assert db_association.updated_at == time


@pytest.mark.asyncio
async def test_create_project(session, mock_db_time, user):
    with mock_db_time(model=Project) as time:
        new_project = Project(name='Branding Agent AI', created_by=user.id)
        session.add(new_project)
        await session.commit()

    db_project = await session.scalar(
        select(Project).where(Project.name == 'Branding Agent AI')
    )

    assert db_project is not None
    assert db_project.name == 'Branding Agent AI'
    assert db_project.created_by == user.id
    assert db_project.created_at == time
    assert db_project.updated_at == time


@pytest.mark.asyncio
async def test_create_project_member(
    session, mock_db_time, user, project, role
):
    with mock_db_time(model=ProjectMembers) as time:
        member_binding = ProjectMembers(
            user_id=user.id, project_id=project.id, role_id=role.id
        )
        session.add(member_binding)
        await session.commit()

    db_member = await session.scalar(
        select(ProjectMembers).where(
            ProjectMembers.user_id == user.id,
            ProjectMembers.project_id == project.id,
        )
    )

    assert db_member is not None
    assert db_member.user_id == user.id
    assert db_member.project_id == project.id
    assert db_member.role_id == role.id
    assert db_member.created_at == time
    assert db_member.updated_at == time


@pytest.mark.asyncio
async def test_create_ai_agent(session, mock_db_time):
    with mock_db_time(model=AiAgent) as time:
        new_agent = AiAgent(
            name='Copwrite_Agent',
            profile_pic='https://image.png',
            description='Agente focado em naming e slogans.',
            system_prompt='Atue como um redator publicitário sênior...',
        )
        session.add(new_agent)
        await session.commit()

    db_agent = await session.scalar(
        select(AiAgent).where(AiAgent.name == 'Copwrite_Agent')
    )

    assert db_agent is not None
    assert db_agent.name == 'Copwrite_Agent'
    assert db_agent.description == 'Agente focado em naming e slogans.'
    assert db_agent.created_at == time
    assert db_agent.updated_at == time


@pytest.mark.asyncio
async def test_create_chat_session(session, mock_db_time, user, project):
    with mock_db_time(model=ChatSession) as time:
        new_session = ChatSession(
            title='Discussão sobre Logotipo',
            started_by=user.id,
            project_id=project.id,
        )
        session.add(new_session)
        await session.commit()

    db_session = await session.scalar(
        select(ChatSession).where(
            ChatSession.title == 'Discussão sobre Logotipo'
        )
    )

    assert db_session is not None
    assert db_session.title == 'Discussão sobre Logotipo'
    assert db_session.started_by == user.id
    assert db_session.project_id == project.id
    assert db_session.created_at == time
    assert db_session.updated_at == time


@pytest.mark.asyncio
async def test_create_message_from_ai(
    session, mock_db_time, chat_session, ai_agent
):
    with mock_db_time(model=Message) as time:
        msg = Message(
            chat_session_id=chat_session.id,
            content='Sugiro utilizar tons de azul e cinza espacial.',
        )
        msg.sender_type = Message.SenderType.AI
        msg.sender_ai_id = ai_agent.id
        session.add(msg)
        await session.commit()

    db_msg = await session.scalar(
        select(Message).where(Message.sender_ai_id == ai_agent.id)
    )

    assert db_msg is not None
    assert db_msg.sender_type == Message.SenderType.AI
    assert db_msg.sender_user_id is None
    assert db_msg.content == 'Sugiro utilizar tons de azul e cinza espacial.'
    assert db_msg.created_at == time
    assert db_msg.updated_at == time
