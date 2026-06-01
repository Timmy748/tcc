from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from api.database import table_registry
from api.models.base import TimestampMixin


@table_registry.mapped_as_dataclass
class ProjectMembers(TimestampMixin):
    __tablename__ = 'project_members'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE')
    )
    project_id: Mapped[int] = mapped_column(
        ForeignKey('projects.id', ondelete='CASCADE')
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey('roles.id', ondelete='CASCADE')
    )

    __table_args__ = (
        UniqueConstraint('user_id', 'project_id', name='uq_user_project'),
    )
