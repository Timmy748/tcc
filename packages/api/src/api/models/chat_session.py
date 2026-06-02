from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from api.database import table_registry
from api.models.base import TimestampMixin


@table_registry.mapped_as_dataclass
class ChatSession(TimestampMixin):
    __tablename__ = 'chat_sessions'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str]
    started_by: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE')
    )
    project_id: Mapped[int] = mapped_column(
        ForeignKey('projects.id', ondelete='CASCADE')
    )
