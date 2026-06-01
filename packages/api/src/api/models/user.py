from sqlalchemy.orm import Mapped, mapped_column

from api.database import table_registry
from api.models.base import TimestampMixin


@table_registry.mapped_as_dataclass
class User(TimestampMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
