from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

from api.settings import Settings

hasher = Argon2Hasher(
    memory_cost=51200, time_cost=4, parallelism=4, hash_len=32
)
settings = Settings()
password_hasher = PasswordHash(hashers=[hasher])


def get_password_hash(plain_password: str) -> str:
    """Retorna a senha Encriptografada.

    Concatena a senha pura com um PEPPER e encriptografa usando o algoritimo do
    argon2 a senha.

    Params:
        plain_password(str): senha pura.
    Returns:
        str: senha concatenada com PEPPER e encriptografada.
    """
    return password_hasher.hash(settings.PEPPER + plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha pura é igual a senha encriptografada.

    Verifica se a senha concatenada com o PEPPER é igual a uma senha já
    encriptografada passada no parâmetro hashed_password.

    Params:
        plain_password(str): senha pura.
        hashed_password(str): senha já encriptografada.
    Returns:
        bool: returna True se forem iguais e False caso sejam diferentes.
    """
    return password_hasher.verify(
        settings.PEPPER + plain_password, hashed_password
    )
