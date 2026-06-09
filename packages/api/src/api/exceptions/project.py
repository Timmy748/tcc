from api.exceptions.base import EntityAlreadyExistsError, EntityNotFoundError


class ProjectNotFoundError(EntityNotFoundError):
    """Erro lançado quando um projeto específico não existe."""

    def __init__(self) -> None:
        super().__init__('Projeto não encontrado.')


class ProjectAlreadyExistsError(EntityAlreadyExistsError):
    """Lançado quando o nome do projeto já foi usado pelo mesmo usuário."""

    def __init__(self):
        super().__init__('Não é possível criar um projeto com mesmo nome.')
