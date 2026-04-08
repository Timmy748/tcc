from dataclasses import asdict

import pytest
from sqlalchemy import select

from api.dependecies import get_user_service
from api.exceptions.base import ForbiddenError
from api.exceptions.user import UserAlreadyExistsError, UserNotFoundError
from api.models.user import User
from api.services.user import UserService
from tests.factories import UserFactory


@pytest.mark.asyncio
async def test_create_user_successfully(
    password_hash_patch, session, mock_db_time
):
    user_service = UserService(session)

    email = 'user@mail.com'
    username = 'name'
    password = 'password'

    with mock_db_time(model=User) as time:
        user = await user_service.create_user(
            email=email, username=username, password=password
        )

    assert asdict(user) == {
        'id': 1,
        'username': username,
        'email': email,
        'password': password,
        'created_at': time,
        'updated_at': time,
    }


@pytest.mark.asyncio
async def test_create_user_saves_on_database(session):
    user_service = UserService(session)

    email = 'user@mail.com'
    username = 'name'
    password = 'password'

    user = await user_service.create_user(
        email=email, username=username, password=password
    )

    await session.flush()
    session.expire_all()

    user_db = await session.scalar(
        select(User).where(User.username == username)
    )

    assert asdict(user_db) == asdict(user)


@pytest.mark.asyncio
async def test_create_user_raises_error_when_email_already_exists(
    user, session
):
    user_service = UserService(session)

    with pytest.raises(UserAlreadyExistsError):
        await user_service.create_user(
            email=user.email, username='a', password='123'
        )


@pytest.mark.asyncio
async def test_create_user_raises_error_when_username_already_exists(
    user, session
):
    user_service = UserService(session)

    with pytest.raises(UserAlreadyExistsError):
        await user_service.create_user(
            email='a', username=user.username, password='123'
        )


@pytest.mark.asyncio
async def test_delete_user_successfully(session, user):
    user_service = UserService(session)
    await user_service.delete_user(user_id=user.id, requester_id=user.id)

    user_db = await session.scalar(select(User).where(User.id == user.id))

    assert user_db is None


@pytest.mark.asyncio
async def test_delete_user_raises_error_when_requester_is_not_owner(
    session, user
):
    user_service = UserService(session)

    with pytest.raises(ForbiddenError, match='Ação não permitida.'):
        await user_service.delete_user(
            user_id=user.id, requester_id=user.id + 1
        )


@pytest.mark.asyncio
async def test_delete_user_raises_error_for_non_existent_id(session):
    user_service = UserService(session)

    with pytest.raises(UserNotFoundError):
        await user_service.delete_user(user_id=1, requester_id=1)


@pytest.mark.asyncio
async def test_update_user_successfully(password_hash_patch, session, user):
    user_service = UserService(session)

    new_username = 'user123'
    new_email = 'user123@mail.com'
    new_password = 'senha123'

    updated_user = await user_service.update_user(
        user_id=user.id,
        requester_id=user.id,
        username=new_username,
        password=new_password,
        email=new_email,
    )

    assert asdict(updated_user) == {
        'id': user.id,
        'username': new_username,
        'email': new_email,
        'password': new_password,
        'created_at': updated_user.created_at,
        'updated_at': updated_user.updated_at,
    }


@pytest.mark.asyncio
async def test_update_user_raises_error_when_id_not_found(session):
    user_service = UserService(session)

    with pytest.raises(UserNotFoundError):
        await user_service.update_user(
            user_id=1, requester_id=1, username='aaa'
        )


@pytest.mark.asyncio
async def test_update_user_ignores_extra_fields_not_in_model(session, user):
    user_service = UserService(session)

    old_user_infos = asdict(user)

    updated_user = await user_service.update_user(
        user_id=user.id, requester_id=user.id, banana='bananinhas'
    )

    assert asdict(updated_user) == old_user_infos


@pytest.mark.asyncio
async def test_update_user_raises_error_when_requester_is_not_owner(
    session, user
):
    user_service = UserService(session)

    with pytest.raises(ForbiddenError, match='Ação não permitida.'):
        await user_service.update_user(
            user_id=user.id, requester_id=user.id + 1, username='user123'
        )


@pytest.mark.asyncio
async def test_update_user_raises_error_when_email_already_exists(
    user, session, other_user
):
    user_service = UserService(session)

    with pytest.raises(UserAlreadyExistsError):
        await user_service.update_user(
            user_id=user.id, requester_id=user.id, email=other_user.email
        )


@pytest.mark.asyncio
async def test_update_user_raises_error_when_username_already_exists(
    user, session, other_user
):
    user_service = UserService(session)

    with pytest.raises(UserAlreadyExistsError):
        await user_service.update_user(
            user_id=user.id, requester_id=user.id, username=other_user.username
        )


@pytest.mark.asyncio
async def test_update_user_prevents_primary_key_modification(session, user):
    user_service = UserService(session)

    old_user_infos = asdict(user)

    updated_user = await user_service.update_user(
        user_id=user.id, requester_id=user.id, id=9
    )

    assert asdict(updated_user) == old_user_infos


@pytest.mark.asyncio
async def test_get_all_returns_empty_list_when_no_users(session):
    user_service = UserService(session)

    expect = 0
    result = await user_service.get_all()

    assert len(result) == expect


@pytest.mark.asyncio
async def test_get_all_returns_list_of_users_when_data_exists(session, user):
    user_service = UserService(session)

    result = await user_service.get_all()

    assert result == [user]


@pytest.mark.asyncio
async def test_get_all_filters_users_by_email_should_returns_1_users(session):
    user_service = UserService(session)

    email_filter = 'bananinha'
    session.add_all(UserFactory.create_batch(5))
    session.add(UserFactory(email=f'{email_filter}@gmail.com'))

    await session.commit()

    expect = 1
    result = await user_service.get_all(email=email_filter)

    assert len(result) == expect


@pytest.mark.asyncio
async def test_get_all_filters_users_by_username_should_returns_1_users(
    session,
):
    user_service = UserService(session)

    username_filter = 'bananinha'
    session.add_all(UserFactory.create_batch(5))
    session.add(UserFactory(username=f'user_{username_filter}'))

    await session.commit()

    expect = 1
    result = await user_service.get_all(username=username_filter)

    assert len(result) == expect


@pytest.mark.asyncio
async def test_get_by_id_returns_user_successfully(session, user):
    user_service = UserService(session)

    searched_user = await user_service.get_by_id(user_id=user.id)

    assert searched_user == user


@pytest.mark.asyncio
async def test_get_by_id_returns_none_for_non_existent_id(session):
    user_service = UserService(session)

    searched_user = await user_service.get_by_id(user_id=1)

    assert searched_user is None


@pytest.mark.asyncio
async def test_get_user_service_return_UserService(session):
    service = await get_user_service(session)
    assert isinstance(service, UserService)
