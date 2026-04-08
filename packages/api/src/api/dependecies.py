from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_session
from api.services.user import UserService, UserServiceProtocol

type AsyncSessionDependency = Annotated[AsyncSession, Depends(get_session)]


async def get_user_service(
    session: AsyncSessionDependency,
) -> UserServiceProtocol:
    """Retorna UserService."""
    return UserService(session=session)


type UserServiceDependency = Annotated[
    UserServiceProtocol, Depends(get_user_service)
]
