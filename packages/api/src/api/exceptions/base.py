class EntityNotFoundError(Exception):
    """Classe base para erros de recursos não encontrados."""

    def __init__(self, message: str = 'Recurso não encontrado.') -> None:
        super().__init__(message)


class EntityAlreadyExistsError(Exception):
    """Base para erros de duplicidade."""

    def __init__(self, message: str = 'Recurso já existe.') -> None:
        super().__init__(message)
