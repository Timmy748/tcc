from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Request, Response

from api.dependecies import AuthServiceDependecy, UserServiceDependency
from api.schemas.user import LoginSchema

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/token', status_code=HTTPStatus.CREATED)
async def login(
    response: Response,
    login: LoginSchema,
    user_service: UserServiceDependency,
    auth_service: AuthServiceDependecy,
):
    try:
        user_id = await user_service.autenticate(
            email=login.email, password=login.password
        )

        access_token = auth_service.create_access_token(user_id=user_id)
        refresh_token = auth_service.create_refresh_token(user_id=user_id)

        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=True,
            samesite='lax',
            max_age=auth_service.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite='lax',
            path='/auth/refresh',
            max_age=auth_service.REFRESH_TOKEN_EXPIRE_DAYS * 60 * 60 * 24,
        )

        return {'message': 'Token criado'}

    except PermissionError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Senha ou Email incorreto',
        )


@router.post('/refresh', status_code=HTTPStatus.CREATED)
async def refresh_access_token(
    request: Request, response: Response, auth_service: AuthServiceDependecy
):
    refresh_token = request.cookies.get('refresh_token')

    if not refresh_token:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail='Refresh token ausente'
        )

    try:
        user_id = auth_service.verify_token(refresh_token)

        new_access_token = auth_service.create_access_token(user_id)
        new_refresh_token = auth_service.create_refresh_token(user_id)

        response.set_cookie(
            key='access_token',
            value=new_access_token,
            httponly=True,
            secure=True,
            samesite='lax',
            max_age=auth_service.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

        response.set_cookie(
            key='refresh_token',
            value=new_refresh_token,
            httponly=True,
            secure=True,
            samesite='lax',
            path='/auth/refresh',
            max_age=auth_service.REFRESH_TOKEN_EXPIRE_DAYS * 60 * 60 * 24,
        )

        return {'message': 'Token criado'}

    except ValueError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Refresh token inválido ou expirado',
        )


@router.post('/logout', status_code=HTTPStatus.OK)
async def logout(response: Response):
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token', path='/auth/refresh')
    return {'message': 'Desconectado'}
