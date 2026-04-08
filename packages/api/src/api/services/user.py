from abc import abstractmethod
from typing import Any, Protocol, Sequence, override

from sqlalchemy import exists, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.exceptions.base import ForbiddenError
from api.exceptions.user import UserAlreadyExistsError, UserNotFoundError
from api.models.user import User
from api.security import get_password_hash


class UserServiceProtocol(Protocol):
    """Interface gerenciar modelo de usuários do sistema."""

    @abstractmethod
    async def get_all(
        self, email: str | None = None, username: str | None = None
    ) -> Sequence[User]:
        """Busca os usuários do sistema podendo filtrar por email ou username.

        Args:
            email(str | None): filtro opcional de email.
            username(str | None): filtro opcional de username.

        Returns:
            Sequence[User]: uma sequência com todos os objetos User encontrados.

        """
        ...

    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None:
        """Busca um único usuário pelo id.

        Args:
            user_id(int): id do usuário a ser buscado.

        Returns:
            User | None: retorna o objeto User encontrado ou None caso não
             encontre nenhum.

        """
        ...

    @abstractmethod
    async def update_user(
        self, user_id: int, requester_id: int, **data: Any
    ) -> User:
        """Atualiza um usuário com as informações passadas em data.

        Args:
            user_id(int): id do usuário a ser atualizado.
            requester_id(int): id do usuário que que quer atualizar o outro.
            data(Any): informações que serão atualizadas no usuário.

        Returns:
            User: objeto User já atualizado com as novas informações.

        Raises:
            UserAlreadyExistsError: se tentar atualizar com um email ou
            username já usado.
            UserNotFoundError: se não encontrar o usuário a ser atualizado.
            PermissionError: se o outro usuário não tiver permissão pra
            atualizar o outro.
        """
        ...

    @abstractmethod
    async def create_user(
        self, email: str, username: str, password: str
    ) -> User:
        """Cria um usuário e salva no banco de dados.

        Args:
            email(str): email único.
            username(str): nome de usuário único.
            password(str): senha em texto simples.

        Returns:
            User: objeto User que foi criado e salvado no banco de dados.

        Raises:
            UserAlreadyExistsError: se tentar criar um usuário com um email ou
            username já usado.
        """
        ...

    @abstractmethod
    async def delete_user(self, user_id: int, requester_id: int) -> None:
        """Deleta um usuário.

        Args:
            user_id(int): id do usuário a ser deletado.
            requester_id: id do usuário que deseja deletar o outro.

        Returns:
            None: retorna None independente se deletar ou não.

        Raises:
            UserNotFoundError: se não encontrar o usuário a ser deletado.
            PermissionError: se o outro usuário não tiver permissão pra deletar
            o outro.
        """
        ...


class UserService(UserServiceProtocol):
    """Implementação do UserServiceProtocol usando o sqlalchemy."""

    def __init__(self, session: AsyncSession):
        self.session = session

    @override
    async def get_all(
        self, email: str | None = None, username: str | None = None
    ) -> Sequence[User]:
        query = select(User)

        if email:
            query = query.where(User.email.contains(email))

        if username:
            query = query.where(User.username.contains(username))

        result = await self.session.scalars(query)

        return result.all()

    async def get_by_id(self, user_id: int) -> User | None:
        query = select(User).where(User.id == user_id)
        result = await self.session.scalar(query)

        return result

    async def update_user(
        self, user_id: int, requester_id: int, **data: Any
    ) -> User:
        if user_id != requester_id:
            raise ForbiddenError('Ação não permitida.')

        user = await self.get_by_id(user_id)

        if not user:
            raise UserNotFoundError()

        try:
            for field, value in data.items():
                if field == 'id':
                    continue

                if field == 'password':
                    setattr(user, field, get_password_hash(value))
                    continue

                setattr(user, field, value)

            await self.session.commit()
            await self.session.refresh(user)

            return user

        except IntegrityError:
            raise UserAlreadyExistsError()

    @override
    async def create_user(
        self, email: str, username: str, password: str
    ) -> User:
        query_existing_user = select(
            exists().where((User.email == email) | (User.username == username))
        )
        existing_user = await self.session.scalar(query_existing_user)

        if existing_user:
            raise UserAlreadyExistsError()

        user = User(
            username=username, email=email, password=get_password_hash(password)
        )

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user

    @override
    async def delete_user(self, user_id: int, requester_id: int) -> None:
        if user_id != requester_id:
            raise ForbiddenError('Ação não permitida.')

        user = await self.get_by_id(user_id)

        if not user:
            raise UserNotFoundError()

        await self.session.delete(user)
        await self.session.commit()
