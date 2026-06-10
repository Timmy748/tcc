from abc import abstractmethod
from datetime import datetime
from typing import Any, Literal, Protocol, Sequence, override

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.exceptions.base import ForbiddenError
from api.exceptions.chat_session import ChatSessionNotFoundError
from api.models.chat_session import ChatSession
from api.models.message import Message
from api.services.permission import PermissionCheckerInterface


class ChatSessionsServiceProtocol(Protocol):
    """Interface para controle de sessões de chat e histórico de mensagens."""

    @abstractmethod
    async def create_chat_session(
        self, project_id: int, user_id: int, title: str
    ) -> ChatSession:
        """Cria uma nova sessão de chat dentro de um projeto.

        Args:
            project_id (int): ID do projeto vinculado.
            user_id (int): ID do usuário criador do chat.
            title (str): Título da sessão de chat.

        Returns:
            ChatSession: A sessão de chat criada.
        """
        ...

    @abstractmethod
    async def delete_chat_session(
        self, chat_id: int, requester_id: int
    ) -> None:
        """Remove uma sessão de chat do sistema.

        Args:
            chat_id (int): ID do chat a ser excluído.
            requester_id (int): ID do usuário solicitando a exclusão.
        """
        ...

    @abstractmethod
    async def update_chat_session(
        self, chat_id: int, requester_id: int, **data: Any
    ) -> ChatSession:
        """Atualiza metadados de uma sessão de chat (como o título).

        Args:
            chat_id (int): ID do chat.
            requester_id (int): ID do usuário editando o chat.
            data (Any): Dados modificados.

        Returns:
            ChatSession: A sessão de chat atualizada.
        """
        ...

    @abstractmethod
    async def get_chats_by_project(
        self,
        project_id: int,
        title: str | None,
        cursor_date: datetime,
        cursor_id: int,
        limit: int,
    ) -> Sequence[ChatSession]:
        """Busca as sessões de chat de um projeto filtrando por título.

        Args:
            project_id (int): ID do projeto.
            title (str): Filtro de busca pelo título do chat.
            cursor_date (datetime): Cursor temporal para paginação.
            cursor_id (int): Cursor de ID para desempate.
            limit (int): Limite de resultados retornados.

        Returns:
            list[ChatSession]: Lista de sessões de chat encontradas.
        """
        ...

    @abstractmethod
    async def get_chat_messages(
        self, chat_id: int, project_id: int, requester_id: int
    ) -> Sequence[Message]:
        """Recupera o histórico de mensagens de uma sessão de chat.

        Args:
            chat_id (int): ID do chat.

        Returns:
            list[Message]: Lista contendo as mensagens do chat.
        """
        ...

    @abstractmethod
    async def save_message(
        self,
        chat_id: int,
        content: str,
        type_sender: Literal['AI', 'USER'],
        sender_id: int,
    ) -> Message:
        """Salva uma nova mensagem enviada no chat.

        Args:
            chat_id (int): ID do chat onde a mensagem foi enviada.
            content (str): Conteúdo textual da mensagem.
            type_sender (Literal["AI", "USER"]): Quem enviou a mensagem.
            sender_id (int): ID do emissor (seja IA ou Usuário).

        Returns:
            Message: O objeto da mensagem salva.
        """
        ...


class ChatSessionsService(ChatSessionsServiceProtocol):
    def __init__(
        self,
        session: AsyncSession,
        permission_checker: PermissionCheckerInterface,
    ) -> None:
        self.session = session
        self.permission_checker = permission_checker

    @override
    async def create_chat_session(
        self, project_id: int, user_id: int, title: str
    ) -> ChatSession:
        has_permission = await self.permission_checker.has_permission(
            project_id=project_id,
            member_id=user_id,
            permission='chat:create',
        )
        if not has_permission:
            raise ForbiddenError()

        chat_session = ChatSession(
            project_id=project_id, started_by=user_id, title=title
        )

        self.session.add(chat_session)
        await self.session.commit()
        await self.session.refresh(chat_session)

        return chat_session

    @override
    async def delete_chat_session(
        self, chat_id: int, requester_id: int
    ) -> None:
        query = select(ChatSession).where(ChatSession.id == chat_id)
        chat_db = await self.session.scalar(query)

        if chat_db is None:
            raise ChatSessionNotFoundError()

        has_permission = await self.permission_checker.has_permission(
            project_id=chat_db.project_id,
            member_id=requester_id,
            permission='chat:delete',
        )
        if not has_permission:
            raise ForbiddenError()

        await self.session.delete(chat_db)
        await self.session.commit()

    @override
    async def update_chat_session(
        self, chat_id: int, requester_id: int, **data: Any
    ) -> ChatSession:
        query = select(ChatSession).where(ChatSession.id == chat_id)
        chat_db = await self.session.scalar(query)

        if chat_db is None:
            raise ChatSessionNotFoundError()

        has_permission = await self.permission_checker.has_permission(
            project_id=chat_db.project_id,
            member_id=requester_id,
            permission='chat:update',
        )
        if not has_permission:
            raise ForbiddenError()

        for field, value in data.items():
            if field in ('id', 'project_id', 'created_by'):
                continue
            setattr(chat_db, field, value)

        await self.session.commit()
        await self.session.refresh(chat_db)

        return chat_db

    @override
    async def get_chats_by_project(
        self,
        project_id: int,
        title: str | None,
        cursor_date: datetime | None,
        cursor_id: int | None,
        limit: int,
    ) -> Sequence[ChatSession]:
        query = select(ChatSession).where(ChatSession.project_id == project_id)

        if title:
            query = query.where(ChatSession.title.ilike(f'%{title}%'))

        if cursor_date and cursor_id:
            query = query.where(
                (ChatSession.created_at < cursor_date)
                | (
                    (ChatSession.created_at == cursor_date)
                    & (ChatSession.id > cursor_id)
                )
            )

        query = query.order_by(
            ChatSession.created_at.desc(), ChatSession.id.asc()
        ).limit(limit + 1)

        result = await self.session.scalars(query)
        return result.all()

    @override
    async def get_chat_messages(
        self, chat_id: int, project_id: int, requester_id: int
    ) -> Sequence[Message]:
        has_permission = await self.permission_checker.has_permission(
            project_id=project_id,
            member_id=requester_id,
            permission='chat:read',
        )
        if not has_permission:
            raise ForbiddenError()
        query = (
            select(Message)
            .where(Message.chat_session_id == chat_id)
            .order_by(Message.created_at.asc())
        )

        result = await self.session.scalars(query)
        return result.all()

    @override
    async def save_message(
        self,
        chat_id: int,
        content: str,
        type_sender: Literal['AI', 'USER'],
        sender_id: int,
    ) -> Message:
        message = Message(
            chat_session_id=chat_id,
            content=content,
        )

        if type_sender == 'AI':
            message.sender_type = Message.SenderType.AI
            message.sender_ai_id = sender_id
        else:
            message.sender_type = Message.SenderType.USER
            message.sender_user_id = sender_id

        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)

        return message
