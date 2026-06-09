from datetime import datetime

import pytest
from sqlalchemy import select

from api.exceptions.base import ForbiddenError
from api.exceptions.project import (
    ProjectAlreadyExistsError,
    ProjectNotFoundError,
)
from api.models.project import Project
from api.models.project_members import ProjectMembers
from api.services.project import ProjectService
from tests.factories import ProjectFactory, ProjectMembersFactory


@pytest.mark.asyncio
async def test_get_projects_by_member_success(
    session, mock_permission_checker, project_member
):
    service = ProjectService(session, mock_permission_checker)

    result = await service.get_projects_by_member(project_member.user_id)

    assert len(result) == 1


@pytest.mark.asyncio
async def test_create_project_success(
    session, mock_permission_checker, user, role
):
    role.name = 'ADMIN'
    await session.commit()
    service = ProjectService(session, mock_permission_checker)

    project = await service.create_project(name='Novo Projeto', user_id=user.id)

    assert project.name == 'Novo Projeto'


@pytest.mark.asyncio
async def test_create_project_already_exists(
    session, mock_permission_checker, project
):
    service = ProjectService(session, mock_permission_checker)

    with pytest.raises(ProjectAlreadyExistsError):
        await service.create_project(
            name=project.name, user_id=project.created_by
        )


@pytest.mark.asyncio
async def test_create_project_internal_error_when_role_none(
    session, mock_permission_checker, user
):
    service = ProjectService(session, mock_permission_checker)

    with pytest.raises(Exception, match='Erro interno.'):
        await service.create_project(name='Projeto Sem Role', user_id=user.id)


@pytest.mark.asyncio
async def test_delete_project_success(
    session, mock_permission_checker, project
):
    service = ProjectService(session, mock_permission_checker)

    await service.delete_project(
        project_id=project.id, requester_id=project.created_by
    )

    db_project = await session.scalar(
        select(Project).where(Project.id == project.id)
    )
    assert db_project is None


@pytest.mark.asyncio
async def test_delete_project_not_found(session, mock_permission_checker):
    service = ProjectService(session, mock_permission_checker)

    with pytest.raises(ProjectNotFoundError):
        await service.delete_project(project_id=999, requester_id=1)


@pytest.mark.asyncio
async def test_delete_project_permission_error_not_owner(
    session, mock_permission_checker, project, other_user
):
    service = ProjectService(session, mock_permission_checker)

    with pytest.raises(
        PermissionError, match='Apenas o dono pode deletar o projeto.'
    ):
        await service.delete_project(
            project_id=project.id, requester_id=other_user.id
        )


@pytest.mark.asyncio
async def test_update_project_success(
    session, mock_permission_checker, project
):
    service = ProjectService(session, mock_permission_checker)

    updated = await service.update_project(
        project_id=project.id,
        requester_id=project.created_by,
        name='Nome Atualizado',
    )

    assert updated.name == 'Nome Atualizado'


@pytest.mark.asyncio
async def test_update_project_integrity_error_raises_already_exists(
    session, mock_permission_checker, project, user
):
    service = ProjectService(session, mock_permission_checker)

    outro_projeto = ProjectFactory(created_by=user.id, name='Projeto Duplicado')
    session.add(outro_projeto)
    await session.commit()

    with pytest.raises(ProjectAlreadyExistsError):
        await service.update_project(
            project_id=project.id,
            requester_id=project.created_by,
            name='Projeto Duplicado',
        )


@pytest.mark.asyncio
async def test_update_project_ignores_id_field(
    session, mock_permission_checker, project
):
    service = ProjectService(session, mock_permission_checker)
    id_original = project.id

    projeto_atualizado = await service.update_project(
        project_id=project.id,
        requester_id=project.created_by,
        id=999,
        name='Apenas o Nome Muda',
    )

    assert projeto_atualizado.id == id_original


@pytest.mark.asyncio
async def test_update_project_not_found(session, mock_permission_checker):
    service = ProjectService(session, mock_permission_checker)

    with pytest.raises(ProjectNotFoundError):
        await service.update_project(
            project_id=999, requester_id=1, name='Novo Nome'
        )


@pytest.mark.asyncio
async def test_update_project_forbidden(
    session, mock_permission_checker, project, other_user
):
    mock_permission_checker.has_permission.return_value = False
    service = ProjectService(session, mock_permission_checker)

    with pytest.raises(ForbiddenError):
        await service.update_project(
            project_id=project.id, requester_id=other_user.id, name='Novo Nome'
        )


@pytest.mark.asyncio
async def test_update_project_permission_error_change_owner(
    session, mock_permission_checker, project, other_user
):
    service = ProjectService(session, mock_permission_checker)

    with pytest.raises(
        PermissionError, match='Apenas o dono pode mudar o dono do projeto.'
    ):
        await service.update_project(
            project_id=project.id,
            requester_id=other_user.id,
            created_by=other_user.id,
        )


@pytest.mark.asyncio
async def test_add_project_member_success(
    session, mock_permission_checker, project, other_user, role
):
    role.name = 'MEMBER'
    await session.commit()
    service = ProjectService(session, mock_permission_checker)

    member = await service.add_project_member(
        project_id=project.id,
        requester_id=project.created_by,
        member_id=other_user.id,
        role='MEMBER',
    )

    assert member.user_id == other_user.id


@pytest.mark.asyncio
async def test_add_project_member_forbidden(
    session, mock_permission_checker, project, other_user
):
    mock_permission_checker.has_permission.return_value = False
    service = ProjectService(session, mock_permission_checker)

    with pytest.raises(ForbiddenError):
        await service.add_project_member(
            project_id=project.id,
            requester_id=project.created_by,
            member_id=other_user.id,
            role='MEMBER',
        )


@pytest.mark.asyncio
async def test_add_project_member_invalid_role(
    session, mock_permission_checker, project, other_user
):
    service = ProjectService(session, mock_permission_checker)

    with pytest.raises(ValueError, match='Role inválida.'):
        await service.add_project_member(
            project_id=project.id,
            requester_id=project.created_by,
            member_id=other_user.id,
            role='ROLE_INEXISTENTE',  # type: ignore
        )


@pytest.mark.asyncio
async def test_remove_project_member_success(
    session, mock_permission_checker, project_member, project
):
    service = ProjectService(session, mock_permission_checker)

    await service.remove_project_member(
        project_id=project.id,
        member_id=project_member.user_id,
        requester_id=project.created_by,
    )

    db_member = await session.scalar(
        select(ProjectMembers).where(
            (ProjectMembers.project_id == project.id)
            & (ProjectMembers.user_id == project_member.user_id)
        )
    )
    assert db_member is None


@pytest.mark.asyncio
async def test_remove_project_member_forbidden(
    session, mock_permission_checker, project, other_user
):
    mock_permission_checker.has_permission.return_value = False
    service = ProjectService(session, mock_permission_checker)

    with pytest.raises(ForbiddenError):
        await service.remove_project_member(
            project_id=project.id,
            member_id=other_user.id,
            requester_id=project.created_by,
        )


@pytest.mark.asyncio
async def test_remove_project_member_not_found(
    session, mock_permission_checker, project
):
    service = ProjectService(session, mock_permission_checker)

    with pytest.raises(ProjectNotFoundError):
        await service.remove_project_member(
            project_id=project.id,
            member_id=999,
            requester_id=project.created_by,
        )


@pytest.mark.asyncio
async def test_alter_project_member_role_success(
    session, mock_permission_checker, project_member, project, role
):
    role.name = 'ADMIN'
    await session.commit()

    service = ProjectService(session, mock_permission_checker)

    updated_member = await service.alter_project_member_role(
        project_id=project.id,
        member_id=project_member.user_id,
        requester_id=project.created_by,
        new_role='ADMIN',
    )

    assert updated_member.role_id == role.id


@pytest.mark.asyncio
async def test_alter_project_member_role_forbidden(
    session, mock_permission_checker, project, other_user
):
    mock_permission_checker.has_permission.return_value = False
    service = ProjectService(session, mock_permission_checker)

    with pytest.raises(ForbiddenError):
        await service.alter_project_member_role(
            project_id=project.id,
            member_id=other_user.id,
            requester_id=project.created_by,
            new_role='ADMIN',
        )


@pytest.mark.asyncio
async def test_alter_project_member_role_invalid_role(
    session, mock_permission_checker, project_member, project
):
    service = ProjectService(session, mock_permission_checker)

    with pytest.raises(ValueError, match='Role inválida.'):
        await service.alter_project_member_role(
            project_id=project.id,
            member_id=project_member.user_id,
            requester_id=project.created_by,
            new_role='ROLE_INEXISTENTE',  # type: ignore
        )


@pytest.mark.asyncio
async def test_alter_project_member_role_member_not_found(
    session, mock_permission_checker, project, role
):
    role.name = 'MEMBER'
    await session.commit()
    service = ProjectService(session, mock_permission_checker)

    with pytest.raises(ProjectNotFoundError):
        await service.alter_project_member_role(
            project_id=project.id,
            member_id=999,
            requester_id=project.created_by,
            new_role='MEMBER',
        )


@pytest.mark.asyncio
async def test_get_all_members_in_project_success(
    session, mock_permission_checker, project_member, project
):
    service = ProjectService(session, mock_permission_checker)

    members = await service.get_all_members_in_project(
        project_id=project.id, cursor_date=None, cursor_id=None, limit=10
    )

    assert len(members) == 1


@pytest.mark.asyncio
async def test_get_all_members_in_project_with_cursor(
    session, mock_permission_checker, project, role, mock_db_time
):
    service = ProjectService(session, mock_permission_checker)

    with mock_db_time(model=ProjectMembers, time=datetime(2026, 1, 2)):
        membro_novo = ProjectMembersFactory(
            project_id=project.id, user_id=10, role_id=role.id
        )
        session.add(membro_novo)
        await session.commit()

    with mock_db_time(model=ProjectMembers, time=datetime(2026, 1, 1)):
        membro_antigo = ProjectMembersFactory(
            project_id=project.id, user_id=11, role_id=role.id
        )
        session.add(membro_antigo)
        await session.commit()

    resultado = await service.get_all_members_in_project(
        project_id=project.id,
        cursor_date=datetime(2026, 1, 2),
        cursor_id=membro_novo.id,
        limit=1,
    )

    assert resultado[0].user_id == membro_antigo.user_id
