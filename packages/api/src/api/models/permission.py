from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database import table_registry
from api.models.base import TimestampMixin

if TYPE_CHECKING:
    from api.models.role_permissions import RolePermissions


@table_registry.mapped_as_dataclass
class Permission(TimestampMixin):
    __tablename__ = 'permissions'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    role_permissions: Mapped[list['RolePermissions']] = relationship(
        back_populates='permission', cascade='all, delete-orphan', init=False
    )
