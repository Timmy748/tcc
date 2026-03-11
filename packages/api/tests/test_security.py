from api.security import get_password_hash, verify_password


def test_password_hashing_is_unique():
    plain_password = 'senha'

    hashed_password_1 = get_password_hash(plain_password)
    hashed_password_2 = get_password_hash(plain_password)

    assert hashed_password_1 != hashed_password_2


def test_password_verification_matches_plain_text_with_hash():
    plain_password = 'senha'
    hashed_password = get_password_hash(plain_password)

    assert verify_password(plain_password, hashed_password)


def test_invalid_password_returns_false():
    wrong_password = 'errado'
    plain_password = 'senha'
    hashed_password = get_password_hash(plain_password)

    assert not verify_password(wrong_password, hashed_password)
