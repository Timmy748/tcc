from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database import table_registry
from api.models.base import TimestampMixin

if TYPE_CHECKING:
    from api.models.role_permissions import RolePermissions


@table_registry.mapped_as_dataclass
class Role(TimestampMixin):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    role_permissions: Mapped[list['RolePermissions']] = relationship(
        argument='RolePermissions', back_populates='role', init=False
    )
