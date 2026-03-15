from api.exceptions.base import EntityAlreadyExistsError, EntityNotFoundError


class UserNotFoundError(EntityNotFoundError):
    """Erro lançado quando um usuário específico não existe."""

    def __init__(self) -> None:
        super().__init__('Usuário não encontrado.')


class UserAlreadyExistsError(EntityAlreadyExistsError):
    """Lançado quando o e-mail ou username já está em uso."""

    def __init__(self):
        super().__init__('Já existe um usuário com esse email ou username.')
