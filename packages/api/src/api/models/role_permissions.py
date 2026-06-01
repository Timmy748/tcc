from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database import table_registry
from api.models.base import TimestampMixin

if TYPE_CHECKING:
    from api.models.permission import Permission
    from api.models.role import Role


@table_registry.mapped_as_dataclass
class RolePermissions(TimestampMixin):
    __tablename__ = 'role_permissions'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    role_id: Mapped[int] = mapped_column(
        ForeignKey('roles.id', ondelete='CASCADE')
    )
    permission_id: Mapped[int] = mapped_column(
        ForeignKey('permissions.id', ondelete='CASCADE')
    )

    role: Mapped['Role'] = relationship(
        init=False, back_populates='role_permissions'
    )
    permission: Mapped['Permission'] = relationship(
        init=False, back_populates='role_permissions'
    )

    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', name='uq_role_permission'),
    )
