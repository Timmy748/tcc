from abc import abstractmethod
from typing import Protocol, override

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.permission import Permission
from api.models.project_members import ProjectMembers
from api.models.role import Role


class PermissionCheckerInterface(Protocol):
    """Interface para verificação de permissões de membros em projetos."""

    @abstractmethod
    async def has_permission(
        self, project_id: int, member_id: int, permission: str
    ) -> bool:
        """Valida se um determinado membro possui a permissão necessária.

        Args:
            project_id (int): ID do projeto.
            member_id (int): ID do membro.
            permission (str): String identificadora da permissão.

        Returns:
            bool: True se tiver permissão, False caso contrário.
        """
        ...


class PermissionCheckerService(PermissionCheckerInterface):
    """Implementação do PermissionCheckerInterface usando o sqlalchemy."""

    def __init__(self, session: AsyncSession):
        self.session = session

    @override
    async def has_permission(
        self, project_id: int, member_id: int, permission: str
    ) -> bool:
        query = (
            select(ProjectMembers.id)
            .join(Role, ProjectMembers.role_id == Role.id)
            .join(Role.role_permissions)
            .join(Permission)
            .where(
                ProjectMembers.project_id == project_id,
                ProjectMembers.user_id == member_id,
                Permission.name == permission,
            )
        )

        result = await self.session.scalar(query)

        return result is not None
