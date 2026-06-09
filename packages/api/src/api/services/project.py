from abc import abstractmethod
from datetime import datetime
from typing import Any, Literal, Protocol, Sequence, override

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.exceptions.base import ForbiddenError
from api.exceptions.project import (
    ProjectAlreadyExistsError,
    ProjectNotFoundError,
)
from api.models.project import Project
from api.models.project_members import ProjectMembers
from api.models.role import Role
from api.services.permission import PermissionCheckerInterface


class ProjectServiceProtocol(Protocol):
    """Interface para gerenciar projetos e seus respectivos membros."""

    @abstractmethod
    async def get_projects_by_member(self, member_id: int) -> Sequence[Project]:
        """Lista todos os projetos que um usuário é membro.

        Args:
            member_id (int): ID do usuário que está nos projetos.

        Returns:
            list[Project]: Lista de projetos que o usuário faz parte.
        """
        ...

    @abstractmethod
    async def create_project(self, name: str, user_id: int) -> Project:
        """Cria um novo projeto associado a um usuário criador.

        Args:
            name (str): Nome do projeto.
            user_id (int): ID do usuário que está criando o projeto.

        Returns:
            Project: O projeto criado.

        Raises:
            ProjectAlreadyExistsError: se um usuário tentar criar um projeto com
            um nome que ele já usou.
        """
        ...

    @abstractmethod
    async def delete_project(self, project_id: int, requester_id: int) -> None:
        """Remove um projeto do sistema validando quem solicitou a exclusão.

        Args:
            project_id (int): ID do projeto a ser deletado.
            requester_id (int): ID do usuário que solicitou a exclusão.
        """
        ...

    @abstractmethod
    async def update_project(
        self, project_id: int, requester_id: int, **data: Any
    ) -> Project:
        """Atualiza os dados de um projeto.

        Args:
            project_id (int): ID do projeto.
            requester_id (int): ID do usuário solicitando a alteração.
            data (Any): Dados a serem modificados.

        Returns:
            Project: O objeto do projeto atualizado.
        """
        ...

    @abstractmethod
    async def add_project_member(
        self,
        project_id: int,
        requester_id: int,
        member_id: int,
        role: Literal['ADMIN', 'MEMBER', 'USER'],
    ) -> ProjectMembers:
        """Adiciona um novo membro ao projeto com uma função específica.

        Args:
            project_id (int): ID do projeto.
            requester_id (int): ID do usuário que está adicionando.
            member_id (int): ID do usuário a ser adicionado como membro.
            role (Literal["ADMIN", "MEMBER", "USER"]): Nível de permissão.

        Returns:
            Member: O vínculo de membro criado.
        """
        ...

    @abstractmethod
    async def remove_project_member(
        self, project_id: int, member_id: int, requester_id: int
    ) -> None:
        """Remove um membro do projeto.

        Args:
            project_id (int): ID do projeto.
            member_id (int): ID do membro a ser removido.
            requester_id (int): ID do usuário que solicitou a remoção.
        """
        ...

    @abstractmethod
    async def alter_project_member_role(
        self,
        project_id: int,
        member_id: int,
        requester_id: int,
        new_role: Literal['ADMIN', 'MEMBER', 'USER'],
    ) -> ProjectMembers:
        """Altera a role de um membro existente no projeto.

        Args:
            project_id (int): ID do projeto.
            member_id (int): ID do membro que terá a role alterada.
            requester_id (int): ID do usuário que está alterando.
            new_role (Literal["ADMIN", "MEMBER", "USER"]): Nova role.

        Returns:
            Member: O membro com a role atualizada.
        """
        ...

    @abstractmethod
    async def get_all_members_in_project(
        self,
        project_id: int,
        cursor_date: datetime | None,
        cursor_id: int | None,
        limit: int,
    ) -> Sequence[ProjectMembers]:
        """Lista os membros de um projeto usando paginação por cursor.

        Args:
            project_id (int): ID do projeto.
            cursor_date (datetime): Ponto de corte temporal da paginação.
            cursor_id (int): Ponto de desempate da paginação.
            limit (int): Limite de registros por página.

        Returns:
            list[Member]: Lista de membros do projeto.
        """
        ...


class ProjectService(ProjectServiceProtocol):
    def __init__(
        self,
        session: AsyncSession,
        permission_checker: PermissionCheckerInterface,
    ) -> None:
        self.session = session
        self.permission_checker = permission_checker

    @override
    async def get_projects_by_member(self, member_id: int) -> Sequence[Project]:
        query = (
            select(Project)
            .join(ProjectMembers, ProjectMembers.project_id == Project.id)
            .where(ProjectMembers.user_id == member_id)
        )

        projects_db = await self.session.scalars(query)

        return projects_db.all()

    @override
    async def create_project(self, name: str, user_id: int) -> Project:
        query = select(Project).where(
            (Project.name == name) & (Project.created_by == user_id)
        )

        project_db = await self.session.scalar(query)

        if project_db:
            raise ProjectAlreadyExistsError()

        project = Project(name=name, created_by=user_id)

        query_role_id = select(Role.id).where(Role.name == 'ADMIN')
        role_id = await self.session.scalar(query_role_id)

        if role_id is None:
            raise Exception('Erro interno.')

        self.session.add(project)
        await self.session.flush()

        member = ProjectMembers(
            project_id=project.id, user_id=user_id, role_id=role_id
        )

        self.session.add(member)
        await self.session.commit()
        await self.session.refresh(project)

        return project

    @override
    async def delete_project(self, project_id: int, requester_id: int) -> None:
        query = select(Project).where(Project.id == project_id)
        project_db = await self.session.scalar(query)

        if project_db is None:
            raise ProjectNotFoundError()

        if project_db.created_by != requester_id:
            raise PermissionError('Apenas o dono pode deletar o projeto.')

        await self.session.delete(project_db)
        await self.session.commit()

    @override
    async def update_project(
        self, project_id: int, requester_id: int, **data: Any
    ) -> Project:
        query = select(Project).where(Project.id == project_id)
        project_db = await self.session.scalar(query)

        if project_db is None:
            raise ProjectNotFoundError()

        has_permission = await self.permission_checker.has_permission(
            project_id=project_id,
            member_id=requester_id,
            permission='project:update',
        )

        if not has_permission:
            raise ForbiddenError()

        try:
            for field, value in data.items():
                if field == 'id':
                    continue
                if (
                    field == 'created_by'
                    and project_db.created_by != requester_id
                ):
                    raise PermissionError(
                        'Apenas o dono pode mudar o dono do projeto.'
                    )

                setattr(project_db, field, value)

            await self.session.commit()
            await self.session.refresh(project_db)

            return project_db

        except IntegrityError:
            raise ProjectAlreadyExistsError()

    @override
    async def add_project_member(
        self,
        project_id: int,
        requester_id: int,
        member_id: int,
        role: Literal['ADMIN', 'MEMBER', 'USER'],
    ) -> ProjectMembers:
        has_permission = await self.permission_checker.has_permission(
            project_id=project_id,
            member_id=requester_id,
            permission='project:add_member',
        )

        if not has_permission:
            raise ForbiddenError()

        query = select(Role.id).where(Role.name == role)
        role_id = await self.session.scalar(query)

        if role_id is None:
            raise ValueError('Role inválida.')

        member = ProjectMembers(
            project_id=project_id, user_id=member_id, role_id=role_id
        )

        self.session.add(member)
        await self.session.commit()
        await self.session.refresh(member)

        return member

    @override
    async def remove_project_member(
        self, project_id: int, member_id: int, requester_id: int
    ) -> None:
        has_permission = await self.permission_checker.has_permission(
            project_id=project_id,
            member_id=requester_id,
            permission='project:remove_member',
        )

        if not has_permission:
            raise ForbiddenError()

        query = select(ProjectMembers).where(
            (ProjectMembers.project_id == project_id)
            & (ProjectMembers.user_id == member_id)
        )
        member_db = await self.session.scalar(query)

        if member_db is None:
            raise ProjectNotFoundError()  # trocar por MemberNotFoundError

        await self.session.delete(member_db)
        await self.session.commit()

    @override
    async def alter_project_member_role(
        self,
        project_id: int,
        member_id: int,
        requester_id: int,
        new_role: Literal['ADMIN', 'MEMBER', 'USER'],
    ) -> ProjectMembers:
        has_permission = await self.permission_checker.has_permission(
            project_id=project_id,
            member_id=requester_id,
            permission='project:alter_member',
        )

        if not has_permission:
            raise ForbiddenError()

        query_role_id = select(Role.id).where(Role.name == new_role)
        role_id = await self.session.scalar(query_role_id)

        if role_id is None:
            raise ValueError('Role inválida.')

        query = select(ProjectMembers).where(
            (ProjectMembers.project_id == project_id)
            & (ProjectMembers.user_id == member_id)
        )
        member_db = await self.session.scalar(query)

        if member_db is None:
            raise ProjectNotFoundError()  # trocar por MemberNotFoundError

        member_db.role_id = role_id
        await self.session.commit()
        await self.session.refresh(member_db)

        return member_db

    @override
    async def get_all_members_in_project(
        self,
        project_id: int,
        cursor_date: datetime | None,
        cursor_id: int | None,
        limit: int,
    ) -> Sequence[ProjectMembers]:
        query = select(ProjectMembers).where(
            ProjectMembers.project_id == project_id
        )

        if cursor_date and cursor_id:
            query = query.where(
                (ProjectMembers.created_at < cursor_date)
                | (
                    (ProjectMembers.created_at == cursor_date)
                    & (ProjectMembers.id > cursor_id)
                )
            )

        query = query.order_by(
            ProjectMembers.created_at.desc(), ProjectMembers.id.asc()
        ).limit(limit + 1)

        members_db = await self.session.scalars(query)

        return members_db.all()
