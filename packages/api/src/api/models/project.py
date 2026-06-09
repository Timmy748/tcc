from typing import Optional

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from api.database import table_registry
from api.models.base import TimestampMixin


@table_registry.mapped_as_dataclass
class Project(TimestampMixin):
    __tablename__ = 'projects'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    created_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey('users.id', ondelete='SET NULL')
    )

    __table_args__ = (
        UniqueConstraint('name', 'created_by', name='uq_name_created_by'),
    )
