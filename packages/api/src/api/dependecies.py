from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_session
from api.services.auth import AuthService, AuthServiceInterface
from api.services.user import UserService, UserServiceProtocol
from api.settings import Settings

type AsyncSessionDependency = Annotated[AsyncSession, Depends(get_session)]

settings = Settings()


async def get_user_service(
    session: AsyncSessionDependency,
) -> UserServiceProtocol:
    """Retorna UserService."""
    return UserService(session=session)


type UserServiceDependency = Annotated[
    UserServiceProtocol, Depends(get_user_service)
]


def get_auth_service() -> AuthServiceInterface:
    """Retorna AuthService."""
    return AuthService(
        secret_key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
        access_token_expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_token_expire_days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
    )


type AuthServiceDependecy = Annotated[
    AuthServiceInterface, Depends(get_auth_service)
]
