import pytest
from freezegun import freeze_time
from jwt import encode


def test_create_access_token_should_generate_valid_jwt(auth_service):
    user_id = 42

    token = auth_service.create_access_token(user_id)

    assert isinstance(token, str)


def test_verify_token_with_valid_refresh_token(auth_service):
    user_id = 555
    refresh_token = auth_service.create_refresh_token(user_id)

    decoded_user_id = auth_service.verify_token(refresh_token)

    assert decoded_user_id == user_id


@freeze_time('2026-05-21 10:00:00', tz_offset=0)
def test_verify_token_should_fail_when_refresh_token_expires(auth_service):
    user_id = 111
    refresh_token = auth_service.create_refresh_token(user_id)

    with freeze_time('2026-05-28 10:01:00', tz_offset=0):
        with pytest.raises(
            ValueError, match='Não foi possivel validar as credenciais.'
        ):
            auth_service.verify_token(refresh_token)


def test_verify_token_should_return_user_id_when_token_is_valid(auth_service):
    user_id = 123
    token = auth_service.create_access_token(user_id)

    decoded_user_id = auth_service.verify_token(token)

    assert decoded_user_id == user_id


def test_verify_token_should_raise_value_error_when_token_is_invalid(
    auth_service,
):
    invalid_token = 'um.token.completamente_invalido'

    with pytest.raises(
        ValueError, match='Não foi possivel validar as credenciais.'
    ):
        auth_service.verify_token(invalid_token)


def test_verify_token_should_raise_value_error_when_sub_is_missing(
    auth_service,
):
    payload_without_sub = {'exp': 9999999999}
    token_invalido = encode(
        payload_without_sub, auth_service.SECRET_KEY, auth_service.ALGORITHM
    )

    with pytest.raises(
        ValueError, match='Não foi possivel validar as credenciais.'
    ):
        auth_service.verify_token(token_invalido)


@freeze_time('2026-05-18 12:00:00', tz_offset=0)
def test_verify_token_should_raise_value_error_when_token_is_expired(
    auth_service,
):
    user_id = 7
    token = auth_service.create_access_token(user_id)

    with freeze_time('2026-05-18 12:06:00', tz_offset=0):
        with pytest.raises(
            ValueError, match='Não foi possivel validar as credenciais.'
        ):
            auth_service.verify_token(token)
