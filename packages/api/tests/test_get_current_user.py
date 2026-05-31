from http import HTTPStatus

import pytest
from fastapi import HTTPException

from api.dependecies import get_current_user_id


def test_get_current_user_id_successfully(mock_request, mock_auth_service):
    expect_value = 42
    mock_request.cookies = {'access_token': 'token_valido_jwt'}
    mock_auth_service.verify_token.return_value = expect_value

    user_id = get_current_user_id(
        request=mock_request, auth_service=mock_auth_service
    )

    assert user_id == expect_value


def test_get_current_user_id_raises_unauthorized_when_cookie_is_missing(
    mock_request, mock_auth_service
):
    mock_request.cookies = {}

    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id(
            request=mock_request, auth_service=mock_auth_service
        )

    assert {
        'status_code': exc_info.value.status_code,
        'detail': exc_info.value.detail,
    } == {
        'status_code': HTTPStatus.UNAUTHORIZED,
        'detail': 'Não autenticado',
    }


def test_get_current_user_id_raises_unauthorized_when_token_is_invalid(
    mock_request, mock_auth_service
):
    mock_request.cookies = {'access_token': 'token_falso_ou_expirado'}

    mock_auth_service.verify_token.side_effect = ValueError(
        'Não foi possivel validar as credenciais.'
    )

    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id(
            request=mock_request, auth_service=mock_auth_service
        )

    assert {
        'status_code': exc_info.value.status_code,
        'detail': exc_info.value.detail,
    } == {
        'status_code': HTTPStatus.UNAUTHORIZED,
        'detail': 'Não autenticado',
    }
