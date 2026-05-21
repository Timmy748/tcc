from abc import abstractmethod
from datetime import datetime, timedelta
from typing import Protocol, override
from zoneinfo import ZoneInfo

from jwt import DecodeError, ExpiredSignatureError, decode, encode


class AuthServiceInterface(Protocol):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    @abstractmethod
    def create_access_token(self, user_id: int) -> str: ...

    @abstractmethod
    def create_refresh_token(self, user_id: int) -> str: ...

    @abstractmethod
    def verify_token(self, token: str) -> int: ...


class AuthService(AuthServiceInterface):
    def __init__(
        self,
        secret_key: str,
        algorithm: str,
        access_token_expire_minutes: int,
        refresh_token_expire_days: int,
    ) -> None:
        self.SECRET_KEY = secret_key
        self.ALGORITHM = algorithm
        self.ACCESS_TOKEN_EXPIRE_MINUTES = access_token_expire_minutes
        self.REFRESH_TOKEN_EXPIRE_DAYS = refresh_token_expire_days

    @override
    def create_access_token(self, user_id: int) -> str:
        expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
            minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode = {'exp': expire, 'sub': str(user_id)}
        token = encode(to_encode, self.SECRET_KEY, self.ALGORITHM)
        return token

    @override
    def create_refresh_token(self, user_id: int) -> str:
        expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
            minutes=self.REFRESH_TOKEN_EXPIRE_DAYS
        )
        to_encode = {'exp': expire, 'sub': str(user_id)}
        token = encode(to_encode, self.SECRET_KEY, self.ALGORITHM)
        return token

    @override
    def verify_token(self, token: str) -> int:
        try:
            payload = decode(
                token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            user_id = payload.get('sub')
            if user_id is None:
                raise ValueError('Não foi possivel validar as credenciais.')
            return int(user_id)
        except (DecodeError, ExpiredSignatureError):
            raise ValueError('Não foi possivel validar as credenciais.')
