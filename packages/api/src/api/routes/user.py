from http import HTTPStatus

from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from api.dependecies import UserServiceDependency
from api.exceptions.base import ForbiddenError
from api.exceptions.user import UserAlreadyExistsError, UserNotFoundError
from api.schemas.user import (
    CreateUserSchema,
    UpdateUserSchema,
    UserListSchema,
    UserPublicSchema,
)

router = APIRouter(prefix='/users', tags=['user'])


@router.get('/', response_model=UserListSchema, status_code=HTTPStatus.OK)
async def get_users(
    user_service: UserServiceDependency,
    username: str | None = None,
    email: str | None = None,
):
    try:
        users = await user_service.get_all(username=username, email=email)

        return {'users': users}
    except Exception:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Erro interno do servidor',
        )


@router.get(
    '/{id}', response_model=UserPublicSchema | None, status_code=HTTPStatus.OK
)
async def get_user(user_service: UserServiceDependency, id: int):
    try:
        user = await user_service.get_by_id(user_id=id)

        return user
    except Exception:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Erro interno do servidor',
        )


@router.post(
    '/', response_model=UserPublicSchema, status_code=HTTPStatus.CREATED
)
async def create_user(
    user_service: UserServiceDependency, data: CreateUserSchema
):
    try:
        user = await user_service.create_user(**data.model_dump())
        return user
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Erro interno do servidor',
        )


@router.delete('/{id}', response_model=None, status_code=HTTPStatus.NO_CONTENT)
async def delete_user(user_service: UserServiceDependency, id: int):
    try:
        await user_service.delete_user(user_id=id, requester_id=id)
    except ForbiddenError as e:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Erro interno do servidor',
        )


@router.put('/{id}', response_model=UserPublicSchema, status_code=HTTPStatus.OK)
async def update_user(
    user_service: UserServiceDependency, id: int, data: UpdateUserSchema
):
    try:
        user = await user_service.update_user(
            user_id=id, requester_id=id, **data.model_dump(exclude_unset=True)
        )

        return user
    except ForbiddenError as e:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e))
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Erro interno do servidor',
        )
