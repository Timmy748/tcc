from http import HTTPStatus


def test_login_should_return_created_status_on_success(
    client, user_service_mock, mock_auth_service
):
    user_service_mock.autenticate.return_value = 1
    mock_auth_service.create_access_token.return_value = 'access_fake'
    mock_auth_service.create_refresh_token.return_value = 'refresh_fake'
    mock_auth_service.ACCESS_TOKEN_EXPIRE_MINUTES = 5
    mock_auth_service.REFRESH_TOKEN_EXPIRE_DAYS = 7

    response = client.post(
        '/auth/token', json={'email': 'test@mail.com', 'password': 'password'}
    )

    assert response.status_code == HTTPStatus.CREATED


def test_login_should_return_correct_message_on_success(
    client, user_service_mock, mock_auth_service
):
    user_service_mock.autenticate.return_value = 1
    mock_auth_service.create_access_token.return_value = 'access_fake'
    mock_auth_service.create_refresh_token.return_value = 'refresh_fake'

    response = client.post(
        '/auth/token', json={'email': 'test@mail.com', 'password': 'password'}
    )

    assert response.json() == {'message': 'Token criado'}


def test_login_should_set_authentication_cookies_on_success(
    client, user_service_mock, mock_auth_service
):
    user_service_mock.autenticate.return_value = 1
    mock_auth_service.create_access_token.return_value = 'meu_access_token'
    mock_auth_service.create_refresh_token.return_value = 'meu_refresh_token'

    mock_auth_service.ACCESS_TOKEN_EXPIRE_MINUTES = 5
    mock_auth_service.REFRESH_TOKEN_EXPIRE_DAYS = 7

    response = client.post(
        '/auth/token', json={'email': 'test@mail.com', 'password': 'password'}
    )

    assert {
        'access_token': response.cookies.get('access_token'),
        'refresh_token': response.cookies.get('refresh_token'),
    } == {
        'access_token': 'meu_access_token',
        'refresh_token': 'meu_refresh_token',
    }


def test_login_should_return_unauthorized_status_when_credentials_are_incorrect(
    client, user_service_mock
):
    user_service_mock.autenticate.side_effect = PermissionError()

    response = client.post(
        '/auth/token', json={'email': 'errado@mail.com', 'password': 'senha'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_login_should_return_unauthorized_detail_when_credentials_are_incorrect(
    client, user_service_mock
):
    user_service_mock.autenticate.side_effect = PermissionError()

    response = client.post(
        '/auth/token', json={'email': 'errado@mail.com', 'password': 'senha'}
    )

    assert response.json()['detail'] == 'Senha ou Email incorreto'


def test_refresh_should_return_created_status_on_success(
    client, mock_auth_service
):
    client.cookies.set('refresh_token', 'token_de_refresh_valido')
    mock_auth_service.verify_token.return_value = 1
    mock_auth_service.create_access_token.return_value = 'novo_access'
    mock_auth_service.create_refresh_token.return_value = 'novo_refresh'
    mock_auth_service.ACCESS_TOKEN_EXPIRE_MINUTES = 5
    mock_auth_service.REFRESH_TOKEN_EXPIRE_DAYS = 7

    response = client.post('/auth/refresh')

    assert response.status_code == HTTPStatus.CREATED


def test_refresh_should_set_new_cookies_on_success(client, mock_auth_service):
    client.cookies.set('refresh_token', 'token_de_refresh_valido')
    mock_auth_service.verify_token.return_value = 1
    mock_auth_service.create_access_token.return_value = 'novo_access'
    mock_auth_service.create_refresh_token.return_value = 'novo_refresh'

    mock_auth_service.ACCESS_TOKEN_EXPIRE_MINUTES = 5
    mock_auth_service.REFRESH_TOKEN_EXPIRE_DAYS = 7

    response = client.post('/auth/refresh')

    assert {
        'access_token': response.cookies.get('access_token'),
        'refresh_token': response.cookies.get('refresh_token'),
    } == {'access_token': 'novo_access', 'refresh_token': 'novo_refresh'}


def test_refresh_should_return_unauthorized_status_when_cookie_is_missing(
    client,
):
    client.cookies.clear()

    response = client.post('/auth/refresh')

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_refresh_should_return_unauthorized_detail_when_cookie_is_missing(
    client,
):
    client.cookies.clear()

    response = client.post('/auth/refresh')

    assert response.json()['detail'] == 'Refresh token ausente'


def test_refresh_should_return_unauthorized_status_when_token_is_invalid(
    client, mock_auth_service
):
    client.cookies.set('refresh_token', 'token_velho_ou_falso')
    mock_auth_service.verify_token.side_effect = ValueError()

    response = client.post('/auth/refresh')

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_refresh_should_return_unauthorized_detail_when_token_is_invalid(
    client, mock_auth_service
):
    client.cookies.set('refresh_token', 'token_velho_ou_falso')
    mock_auth_service.verify_token.side_effect = ValueError()

    response = client.post('/auth/refresh')

    assert response.json()['detail'] == 'Refresh token inválido ou expirado'


def test_logout_should_return_ok_status(client):
    response = client.post('/auth/logout')

    assert response.status_code == HTTPStatus.OK


def test_logout_should_return_correct_message(client):
    response = client.post('/auth/logout')

    assert response.json() == {'message': 'Desconectado'}


def test_logout_should_clear_authentication_cookies(client, mock_auth_service):
    client.cookies.set('access_token', 'token_antigo')
    client.cookies.set('refresh_token', 'token_antigo')

    mock_auth_service.ACCESS_TOKEN_EXPIRE_MINUTES = 5
    mock_auth_service.REFRESH_TOKEN_EXPIRE_DAYS = 7

    response = client.post('/auth/logout')

    assert {
        'access_token': response.cookies.get('access_token'),
        'refresh_token': response.cookies.get('refresh_token'),
    } == {'access_token': None, 'refresh_token': None}
