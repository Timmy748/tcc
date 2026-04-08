import json
from http import HTTPStatus

import pytest

from api.exceptions.base import ForbiddenError
from api.exceptions.user import UserAlreadyExistsError, UserNotFoundError
from api.schemas.user import UserPublicSchema


@pytest.mark.asyncio
async def test_get_users_returns_empty_list_when_no_users_exist(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


@pytest.mark.asyncio
async def test_get_users_returns_list_of_users(client, user, user_service_mock):
    user_service_mock.get_all.return_value = [user]
    user_schema = json.loads(
        UserPublicSchema.model_validate(
            user, from_attributes=True
        ).model_dump_json()
    )

    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


@pytest.mark.asyncio
async def test_get_users_internal_error_on_exception(client, user_service_mock):
    user_service_mock.get_all.side_effect = Exception('Erro')

    response = client.get('/users/')

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response.json() == {'detail': 'Erro interno do servidor'}


@pytest.mark.asyncio
async def test_get_user_by_id_should_return_user_when_exists(
    client, user_service_mock, user
):
    user_service_mock.get_by_id.return_value = user
    user_schema = json.loads(
        UserPublicSchema.model_validate(
            user, from_attributes=True
        ).model_dump_json()
    )

    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


@pytest.mark.asyncio
async def test_get_user_returns_none_when_not_found_user(
    client, user_service_mock
):
    user_service_mock.get_by_id.return_value = None

    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() is None


@pytest.mark.asyncio
async def test_get_user_internal_error_on_exception(client, user_service_mock):
    user_service_mock.get_by_id.side_effect = Exception('Erro')

    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response.json() == {'detail': 'Erro interno do servidor'}


@pytest.mark.asyncio
async def test_delete_user_should_return_no_content_on_success(
    client, user_service_mock, user
):
    user_service_mock.delete_user.return_value = None

    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_delete_user_should_return_forbidden_when_user_is_not_allowed(
    client, user_service_mock
):
    user_service_mock.delete_user.side_effect = ForbiddenError()

    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Ação não permitida.'}


@pytest.mark.asyncio
async def test_delete_user_should_return_not_found_when_user_does_not_exist(
    client, user_service_mock
):
    user_service_mock.delete_user.side_effect = UserNotFoundError()

    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuário não encontrado.'}


@pytest.mark.asyncio
async def test_delete_user_internal_error_on_exception(
    client, user_service_mock
):
    user_service_mock.delete_user.side_effect = Exception('Erro')

    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response.json() == {'detail': 'Erro interno do servidor'}


@pytest.mark.asyncio
async def test_update_user_should_return_updated_user_on_success(
    client, user_service_mock, user
):
    user_service_mock.update_user.return_value = user

    expected_user = json.loads(
        UserPublicSchema.model_validate(
            user, from_attributes=True
        ).model_dump_json()
    )

    response = client.put(
        f'/users/{user.id}',
        json={
            'username': 'test2',
            'email': 'test2@gmail.com',
            'password': None,
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == expected_user


@pytest.mark.asyncio
async def test_update_user_should_return_forbidden_when_user_is_not_allowed(
    client, user_service_mock
):
    user_service_mock.update_user.side_effect = ForbiddenError()

    response = client.put(
        '/users/1',
        json={
            'username': 'test',
            'email': 'test@gmail.com',
            'password': 'senha',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Ação não permitida.'}


@pytest.mark.asyncio
async def test_update_user_should_return_not_found_when_user_does_not_exist(
    client, user_service_mock
):
    user_service_mock.update_user.side_effect = UserNotFoundError()

    response = client.put(
        '/users/1',
        json={
            'username': 'test',
            'email': 'test@gmail.com',
            'password': 'senha',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuário não encontrado.'}


@pytest.mark.asyncio
async def test_update_user_should_return_conflict_when_email_already_exists(
    client, user_service_mock
):
    user_service_mock.update_user.side_effect = UserAlreadyExistsError()

    response = client.put(
        '/users/1',
        json={
            'username': 'test',
            'email': 'test@gmail.com',
            'password': 'senha',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': 'Já existe um usuário com esse email ou username.'
    }


@pytest.mark.asyncio
async def test_update_user_internal_error_on_exception(
    client, user_service_mock
):
    user_service_mock.update_user.side_effect = Exception('Erro')

    response = client.put(
        '/users/1',
        json={
            'username': 'test',
            'email': 'test@gmail.com',
            'password': 'senha',
        },
    )

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response.json() == {'detail': 'Erro interno do servidor'}


@pytest.mark.asyncio
async def test_create_u(client, user_service_mock, user):
    user_service_mock.create_user.return_value = user
    user_schema = json.loads(
        UserPublicSchema.model_validate(
            user, from_attributes=True
        ).model_dump_json()
    )

    response = client.post(
        '/users/',
        json={
            'username': 'test',
            'email': 'test@gmail.com',
            'password': 'senha',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == user_schema


@pytest.mark.asyncio
async def test_create_user_should_return_conflict_when_email_already_exists(
    client, user_service_mock
):
    user_service_mock.create_user.side_effect = UserAlreadyExistsError()

    response = client.post(
        '/users/',
        json={
            'username': 'test',
            'email': 'test@gmail.com',
            'password': 'senha',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': 'Já existe um usuário com esse email ou username.'
    }


@pytest.mark.asyncio
async def test_create_user_internal_error_on_exception(
    client, user_service_mock
):
    user_service_mock.create_user.side_effect = Exception('Erro')

    response = client.post(
        '/users/',
        json={
            'username': 'test',
            'email': 'test@gmail.com',
            'password': 'senha',
        },
    )

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response.json() == {'detail': 'Erro interno do servidor'}
