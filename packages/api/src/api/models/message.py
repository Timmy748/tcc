from enum import StrEnum
from typing import Optional

from sqlalchemy import TEXT, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from api.database import table_registry
from api.models.base import TimestampMixin


@table_registry.mapped_as_dataclass
class Message(TimestampMixin):
    class SenderType(StrEnum):
        AI = 'AI'
        USER = 'USER'

    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    chat_session_id: Mapped[int] = mapped_column(
        ForeignKey('chat_sessions.id', ondelete='CASCADE')
    )
    content: Mapped[str] = mapped_column(TEXT)
    sender_type: Mapped[SenderType] = mapped_column(
        Enum(SenderType, name='sender_type_enum'), init=False
    )

    sender_user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('users.id', ondelete='SET NULL'), init=False
    )
    sender_ai_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('ai_agents.id', ondelete='SET NULL'), init=False
    )
