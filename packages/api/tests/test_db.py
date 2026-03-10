from dataclasses import asdict

import pytest
from sqlalchemy import select

from api.models.user import User


@pytest.mark.asyncio
async def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='João', email='joão@gmail.com', password='senha'
        )
        session.add(new_user)
        await session.commit()

    user = await session.scalar(select(User).where(User.username == 'João'))

    assert asdict(user) == {
        'id': 1,
        'username': 'João',
        'email': 'joão@gmail.com',
        'password': 'senha',
        'created_at': time,
        'updated_at': time,
    }
