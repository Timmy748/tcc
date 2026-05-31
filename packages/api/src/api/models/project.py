from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from api.database import table_registry


@table_registry.mapped_as_dataclass
class project:
    __tablename__ = 'projects'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    created_by: Mapped[int] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
