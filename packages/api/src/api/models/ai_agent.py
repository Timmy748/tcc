from typing import Optional

from sqlalchemy import TEXT
from sqlalchemy.orm import Mapped, mapped_column

from api.database import table_registry
from api.models.base import TimestampMixin


@table_registry.mapped_as_dataclass
class AiAgent(TimestampMixin):
    __tablename__ = 'ai_agents'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    profile_pic: Mapped[Optional[str]]
    description: Mapped[Optional[str]] = mapped_column(TEXT)
    system_prompt: Mapped[Optional[str]] = mapped_column(TEXT)
