from api.exceptions.base import EntityNotFoundError


class ChatSessionNotFoundError(EntityNotFoundError):
    """Erro lançado quando uma sessão de chat específica não existe."""

    def __init__(self) -> None:
        super().__init__('Sessão de chat não encontrado.')
